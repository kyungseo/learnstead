"""고정 응답으로 제어 흐름을 검사한다. 모델 품질을 검증하는 테스트가 아니다."""
import concurrent.futures as futures
from contextlib import redirect_stdout, redirect_stderr
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
from types import SimpleNamespace as NS
import unittest
from unittest.mock import patch

FILE = Path(__file__).with_name('patterns.py')
spec = importlib.util.spec_from_file_location('patterns', FILE)
p = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p)


def response(text='answer', usage=True):
    return NS(choices=[NS(message=NS(content=text))],
              usage=NS(prompt_tokens=7, completion_tokens=3) if usage else None)


def fake_client(fn):
    return NS(chat=NS(completions=NS(create=fn)))


class PatternTests(unittest.TestCase):
    def setUp(self):
        p.reset_stats(); p.BUDGET['tokens'] = 0; p.client = None
        self.stdout = io.StringIO(); self.stderr = io.StringIO()
        self.out = redirect_stdout(self.stdout); self.err = redirect_stderr(self.stderr)
        self.out.__enter__(); self.err.__enter__()
    def tearDown(self):
        self.err.__exit__(None, None, None); self.out.__exit__(None, None, None)
        p.client = None; p.BUDGET['tokens'] = 0
    def main(self, *args):
        with patch.object(sys, 'argv', ['patterns.py', *args]): return p.main()
    def test_concurrent_usage_is_complete(self):
        barrier = threading.Barrier(8)
        def create(**kwargs):
            barrier.wait(timeout=5)
            return response()
        p.client = fake_client(create)
        with futures.ThreadPoolExecutor(max_workers=8) as pool:
            list(pool.map(lambda _: p.ask('s','u','model',quiet=True),range(40)))
        self.assertEqual(p.STATS, dict(calls=40,prompt_tokens=280,completion_tokens=120,usage_missing=0))
    def test_budget_allows_inflight_but_blocks_new_calls(self):
        barrier = threading.Barrier(3)
        def create(**kwargs):
            barrier.wait(timeout=5)
            return response()
        p.client = fake_client(create); p.BUDGET['tokens'] = 5
        with futures.ThreadPoolExecutor(max_workers=3) as pool:
            list(pool.map(lambda _: p.ask('s','u','model'),range(3)))
        self.assertEqual(p.STATS['prompt_tokens']+p.STATS['completion_tokens'],30)
        with self.assertRaises(p.BudgetExceeded): p.ask('s','u','model')
        self.assertEqual(p.STATS['calls'],3)
    def test_missing_usage_stops_budgeted_run(self):
        p.client = fake_client(lambda **kw: response(usage=False)); p.BUDGET['tokens']=100
        with self.assertRaises(p.BudgetExceeded): p.ask('s','u','model')
        with self.assertRaises(p.BudgetExceeded): p.ask('s','u','model')
        self.assertEqual(p.STATS['calls'],1); self.assertEqual(p.STATS['usage_missing'],1)
    def test_missing_usage_is_visible_without_budget(self):
        p.client = fake_client(lambda **kw: response(usage=False))
        self.assertEqual(self.main('single','question','--quiet'),0)
        self.assertIn('토큰 합계 불완전',self.stdout.getvalue())
    def test_invalid_routes_fall_back(self):
        for raw in ('{}','[]','null','{"topic": []}','{"topic":"other","reason":"x"}','{"topic":"휴가-규정","reason":3}'):
            with self.subTest(raw=raw), patch.object(p,'ask',return_value=raw), patch.object(p,'run_single',return_value='fallback') as fallback:
                self.assertEqual(p.run_router('q','m',True),'fallback'); fallback.assert_called_once()
    def test_valid_route_and_not_found_fallback(self):
        replies=['{"topic":"휴가-규정","reason":"휴가 질문"}',p.NOT_FOUND,'full answer']
        with patch.object(p,'ask',side_effect=replies) as ask:
            self.assertEqual(p.run_router('q','m',True,True),'full answer'); self.assertEqual(ask.call_count,3)
    def test_invalid_verdict_never_passes_or_rewrites(self):
        for raw in ('[]','null','{"pass":"false","problem":"x"}','{"pass":1,"problem":"x"}','{"pass":false,"problem":[]}','{"pass":false,"problem":""}'):
            with self.subTest(raw=raw), patch.object(p,'ask',side_effect=['draft',raw]) as ask:
                self.assertEqual(p.run_loop('q','m',False),'draft'); self.assertEqual(ask.call_count,2)
        self.assertNotIn('회차에서 통과',self.stdout.getvalue())
    def test_loop_accepts_boolean_pass(self):
        with patch.object(p,'ask',side_effect=['draft','{"pass":true,"problem":""}']) as ask:
            self.assertEqual(p.run_loop('q','m',True),'draft'); self.assertEqual(ask.call_count,2)
    def test_loop_round_limit_and_repeat_stop(self):
        bad='{"pass":false,"problem":"missing date"}'
        for repeat,expected in ((False,5),(True,4)):
            with patch.object(p,'ask',side_effect=['draft',bad,'revision',bad,'final']) as ask:
                result=p.run_loop('q','m',True,rounds=2,stop_on_repeat=repeat)
                self.assertEqual(ask.call_count,expected)
                self.assertEqual(result,'revision' if repeat else 'final')
    def test_budget_stop_has_nonzero_exit(self):
        p.client=fake_client(lambda **kw: response())
        self.assertEqual(self.main('pipeline','q','--budget-tokens','1','--quiet'),1)
        self.assertEqual(p.STATS['calls'],1)
    def test_all_resets_stats_per_pattern(self):
        def create(**kw):
            schema=kw.get('response_format',{}).get('json_schema',{}).get('schema',{})
            if 'topic' in schema.get('properties',{}): return response('{"topic":"휴가-규정","reason":"x"}')
            if 'pass' in schema.get('properties',{}): return response('{"pass":true,"problem":""}')
            return response('휴가-규정')
        p.client=fake_client(create)
        self.assertEqual(self.main('all','q','--quiet'),0)
        self.assertEqual(p.STATS['calls'],2)
        self.assertIn('[workers] 완료 호출 4회',self.stdout.getvalue())
    def test_batch_validates_whole_file_before_calls(self):
        good={'q':'q','topic':'휴가-규정'}
        with tempfile.TemporaryDirectory() as d:
            file=Path(d)/'questions.json'
            for data in ([],{},None,[good,{'q':'bad','topic':'other'}],[{'q':' ','topic':'휴가-규정'}],[{'q':'q','topic':[]} ]):
                file.write_text(json.dumps(data))
                with self.subTest(data=data),patch.object(p,'classify') as classify,self.assertRaises(SystemExit) as error:
                    self.main('router','--batch',str(file))
                self.assertEqual(error.exception.code,2); classify.assert_not_called()
    def test_batch_budget_stop_has_no_full_accuracy(self):
        with tempfile.TemporaryDirectory() as d:
            file=Path(d)/'q.json';file.write_text(json.dumps([{'q':'q','topic':'휴가-규정'}]*2))
            p.client=fake_client(lambda **kw: response('{"topic":"휴가-규정","reason":"x"}'))
            self.assertEqual(self.main('router','--batch',str(file),'--budget-tokens','1'),1)
            self.assertNotIn('라우터 정확도:',self.stdout.getvalue())
            self.assertIn('전체 정확도 미산출',self.stderr.getvalue())
    def test_cli_rejects_invalid_combinations_without_sdk(self):
        cases=[['loop','q','--rounds','0'],['loop','q','--rounds','-1'],['workers','q','--max-workers','-1'],['single','q','--budget-tokens','-1'],['all','--batch','absent.json'],['router','q','--batch','absent.json'],['router','--batch','absent.json'],['single',' ']]
        for args in cases:
            with self.subTest(args=args):
                r=subprocess.run([sys.executable,str(FILE),*args],capture_output=True,text=True)
                self.assertEqual(r.returncode,2); self.assertNotIn('Traceback',r.stderr)

if __name__ == '__main__': unittest.main()
