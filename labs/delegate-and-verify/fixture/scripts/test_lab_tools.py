"""모델 호출 없이 채점 의미, 실행 실패, 결과 보존과 Git 통합을 검사한다."""
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('score', HERE / 'score.py')
score = importlib.util.module_from_spec(spec)
spec.loader.exec_module(score)

STUB = r'''#!PYTHON
import json, os, pathlib, sys
args = sys.argv[1:]
with open(os.environ['LAB_TEST_LOG'], 'a') as f:
    f.write(json.dumps(args) + '\n')
mode = os.environ.get('LAB_TEST_MODE')
if mode == 'fail': sys.exit(7)
root = pathlib.Path(args[args.index('-C')+1]) if '-C' in args else pathlib.Path.cwd()
if root.name in ('wt-x', 'wt-y'):
    if mode == 'conflict':
        p = root / 'src/ledger/report.py'
        p.write_text(p.read_text().replace('def render(', 'def render_x(' if root.name == 'wt-x' else 'def render_y('))
    elif mode == 'disjoint': (root / (root.name+'.txt')).write_text('stub edit\n')
if pathlib.Path(sys.argv[0]).name == 'claude':
    print(json.dumps({'type':'result','result':'{"findings": []}','usage':{},'modelUsage':{}}))
else:
    print(json.dumps({'type':'item.completed','item':{'type':'agent_message','text':'{"findings": []}'}}))
    print(json.dumps({'type':'turn.completed','usage':{'input_tokens':10}}))
'''

class Contracts(unittest.TestCase):
    def test_scoring_does_not_claim_semantic_correctness(self):
        s = score.judge([{'file':f,'function':fn,'reason':'rename'} for f,fn in score.BUGS])
        self.assertEqual(s['hits'], 3)
        self.assertEqual(s['semantic_correctness'], 'not_evaluated')
        s = score.judge([{'file':'cli.py','function':'main'}])
        self.assertEqual(s['outside_golden'], 1)
        for value in (None, {}, [None], ['bad']): self.assertFalse(score.judge(value)['parsed'])

    def test_process_failure_is_visible_in_summary(self):
        with tempfile.TemporaryDirectory() as tmp:
            r = Path(tmp)/'codex-s01-review-direct-r1'; r.mkdir()
            (r/'exit_code.txt').write_text('7')
            (r/'wall_seconds.txt').write_text('0.2')
            out = subprocess.check_output([sys.executable,str(HERE/'summarize.py'),tmp,'--md'],text=True)
            self.assertIn('exit_code=7',out)
            self.assertIn('s01-review-direct',out)

    def test_unknown_usage_and_conflict(self):
        with tempfile.TemporaryDirectory() as tmp:
            r = Path(tmp)/'codex-s03-samefile-worktree-r1'; r.mkdir()
            for n,v in {'stream-x.jsonl':'','wall_seconds.txt':'2','integration_status.txt':'conflict','tests.txt':'SKIPPED_NOT_INTEGRATED','tests-x.txt':'PASS','tests-y.txt':'PASS'}.items(): (r/n).write_text(v)
            s = score.score(r)
            self.assertFalse(s['usage_available'])
            self.assertEqual(s['tests'], 'SKIPPED_NOT_INTEGRATED')
            self.assertEqual(s['worker_tests'], {'x':'PASS','y':'PASS'})
            out = subprocess.check_output([sys.executable,str(HERE/'score.py'),'--tsv',str(r)],text=True)
            self.assertIn('\tNA\t',out)
            out = subprocess.check_output([sys.executable,str(HERE/'summarize.py'),tmp,'--md'],text=True)
            self.assertIn('conflict',out)
            self.assertIn('— | — | — | —',out)

class Runners(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.root = Path(self.tmp.name); self.fx = self.root/'fixture'
        for n in ('scripts','project','agents','prompts','expected'):
            shutil.copytree(HERE.parent/n,self.fx/n,ignore=shutil.ignore_patterns('__pycache__'))
        b = self.root/'bin'; b.mkdir(); self.log = self.root/'calls'
        for n in ('claude','codex'):
            p=b/n; p.write_text(STUB.replace('PYTHON',sys.executable,1)); p.chmod(0o755)
        self.env=dict(os.environ,PATH=str(b)+os.pathsep+os.environ['PATH'],LAB_TEST_LOG=str(self.log),GIT_CONFIG_NOSYSTEM='1',GIT_CONFIG_GLOBAL=os.devnull,CODEX_HOME=str(self.root/'codex-home'),PYTHONDONTWRITEBYTECODE='1')
        self.env.pop('LAB_TEST_MODE',None)
    def tearDown(self): self.tmp.cleanup()
    def run_script(self,n,*args,**env):
        return subprocess.run(['/bin/bash',str(self.fx/'scripts'/n),*args],cwd=self.fx,env=dict(self.env,**env),capture_output=True,text=True,timeout=30)
    def calls(self): return [json.loads(l) for l in self.log.read_text().splitlines()] if self.log.exists() else []
    def test_batch_single_tool_and_direct_flag(self):
        r=self.run_script('batch.sh','one','1','s01-review-direct','s04-cross-review',LAB_TOOLS='codex')
        self.assertEqual(r.returncode,0,r.stderr); self.assertEqual(len(self.calls()),1)
        self.assertIn('agents.enabled=false',self.calls()[0]); self.assertIn('건너뜁니다',r.stdout)
    def test_no_overwrite_or_invalid_inputs(self):
        p=self.fx/'runs/keep/codex-s01-review-direct-r1'; p.mkdir(parents=True); (p/'sentinel').write_text('keep')
        for n,c in [('keep','1'),('../outside','1'),('valid','0'),('valid','00'),('valid','-1')]:
            r=self.run_script('run-codex.sh','s01-review-direct',n,c); self.assertNotEqual(r.returncode,0)
        self.assertEqual((p/'sentinel').read_text(),'keep'); self.assertFalse(self.calls())
    def test_batch_preflight(self):
        r=self.run_script('batch.sh','unknown','1','s01-review-direct','missing',LAB_TOOLS='codex')
        self.assertNotEqual(r.returncode,0); self.assertFalse(self.calls())
    def test_failure_skips_followup(self):
        for tool in ('claude','codex'):
            r=self.run_script('run-'+tool+'.sh','s04-writer-selfreview','failed','1',LAB_TEST_MODE='fail')
            self.assertEqual(r.returncode,7,r.stderr)
            p=self.fx/f'runs/failed/{tool}-s04-writer-selfreview-r1'
            self.assertEqual((p/'exit_code.txt').read_text().strip(),'7'); self.assertFalse((p/'stream-followup.jsonl').exists())
        self.assertEqual(len(self.calls()),2)
    def test_claude_followup_retains_constraint(self):
        r=self.run_script('run-claude.sh','s04-writer-selfreview','followup','1')
        self.assertEqual(r.returncode,0,r.stderr); self.assertEqual(len(self.calls()),2)
        for c in self.calls(): self.assertIn('--disallowedTools',c); self.assertIn('Agent',c)
    def test_worktree_conflict(self):
        r=self.run_script('run-codex-worktrees.sh','conflict','1',LAB_TEST_MODE='conflict',CODEX_MODEL='test-model',CODEX_EFFORT='high')
        self.assertEqual(r.returncode,0,r.stderr)
        p=self.fx/'runs/conflict/codex-s03-samefile-worktree-r1'
        self.assertEqual((p/'integration_status.txt').read_text().strip(),'conflict')
        self.assertEqual((p/'tests.txt').read_text().strip(),'SKIPPED_NOT_INTEGRATED')
        for c in self.calls(): self.assertIn('test-model',c); self.assertIn('agents.enabled=false',c)
        self.assertGreater(float((p/'wall_total_seconds.txt').read_text()),float((p/'wall_edit_seconds.txt').read_text()))
    def test_worktree_disjoint(self):
        r=self.run_script('run-codex-worktrees.sh','merged','1',LAB_TEST_MODE='disjoint')
        self.assertEqual(r.returncode,0,r.stderr); p=self.fx/'runs/merged/codex-s03-samefile-worktree-r1'
        self.assertEqual((p/'integration_status.txt').read_text().strip(),'merged')
        self.assertEqual((p/'tests.txt').read_text().splitlines()[-1],'PASS')
        self.assertTrue((p/'proj/wt-x.txt').exists()); self.assertTrue((p/'proj/wt-y.txt').exists())
        self.assertTrue(score.score(p)['manual_review_required'])
    def test_worktree_no_change(self):
        r=self.run_script('run-codex-worktrees.sh','unchanged','1')
        self.assertNotEqual(r.returncode,0); p=self.fx/'runs/unchanged/codex-s03-samefile-worktree-r1'
        self.assertEqual((p/'integration_status.txt').read_text().strip(),'commit_failed')
        self.assertEqual((p/'tests.txt').read_text().strip(),'SKIPPED_NOT_INTEGRATED')

if __name__ == '__main__': unittest.main()
