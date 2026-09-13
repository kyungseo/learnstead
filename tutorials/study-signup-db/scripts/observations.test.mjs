import {test} from 'node:test';
import assert from 'node:assert/strict';
import {createObservations} from './observations.mjs';

test('실제 값이 다르면 FAIL을 보여 주고 검증을 중단한다',()=>{
 const lines=[];const {observe,observations}=createObservations(s=>lines.push(s));
 assert.throws(()=>observe('02','행 수',1,2),assert.AssertionError);
 assert.equal(observations[0].passed,false);
 assert.ok(lines.some(s=>s.includes('실제: 2')));
 assert.ok(lines.some(s=>s.includes('FAIL')));
});
test('기록한 변경 전후 값은 이후 객체 수정으로 바뀌지 않는다',()=>{
 const {observe,observations}=createObservations(()=>{});
 const value={rows:[{id:'연습-1',note:''}]};observe('05','기록',value,value);
 value.rows[0].note='수정';assert.equal(observations[0].actual.rows[0].note,'');
});
test('숫자와 문자열을 같은 관찰값으로 통과시키지 않는다',()=>{
 const {observe}=createObservations(()=>{});
 assert.throws(()=>observe('03','행 수',1,'1'),assert.AssertionError);
});
