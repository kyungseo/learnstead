import assert from 'node:assert/strict';
import {isDeepStrictEqual} from 'node:util';

// 호출부에서 고른 연습용 관찰값만 받는다. 인증 응답이나 설정 전체를 전달하지 않는다.
export function createObservations(log = console.log) {
  const observations = [];
  function observe(chapter, label, expected, actual) {
    const entry = structuredClone({chapter, label, expected, actual, passed:isDeepStrictEqual(actual, expected)});
    observations.push(entry);
    log(`관찰 [${chapter}] ${label}`);
    log(`  예상: ${JSON.stringify(entry.expected, null, 2)}`);
    log(`  실제: ${JSON.stringify(entry.actual, null, 2)}`);
    log(`  판정: ${entry.passed ? 'PASS' : 'FAIL'}`);
    assert.deepStrictEqual(actual, expected, `${chapter}: ${label}`);
  }
  return {observations, observe};
}
