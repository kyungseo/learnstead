import assert from 'node:assert/strict';
import {mkdirSync,writeFileSync,readFileSync} from 'node:fs';
import path from 'node:path';
import {status,setup,request,sql,run,app,root,container,password} from './local.mjs';
const cfg=status();
await setup(cfg);
const results=[];
function pass(label) {results.push(label);console.log('PASS '+label);}
const events=['10000000-0000-4000-8000-000000000001','10000000-0000-4000-8000-000000000002','10000000-0000-4000-8000-000000000003'];
const initial=Number(sql('select count(*) from public.registrations'));
assert.equal(initial,0,'verify는 신청 0개인 연습 DB에서 시작합니다. 필요하면 문서의 명시적 로컬 reset을 실행하세요.');
const users=[];
const created=[];
for(const name of ['alice','bob']) {
 const login=await request(cfg,'/auth/v1/token?grant_type=password',{method:'POST',body:{email:name+'@example.com',password}});
 assert.equal(login.status,200); users.push({token:login.data.access_token,id:login.data.user.id});
}
pass('Auth 비밀번호 로그인 A/B 각각 성공');
const [a,b]=users;
const rest=(endpoint,user,method='GET',body)=>request(cfg,'/rest/v1/'+endpoint,{token:user?.token,method,body,prefer:'return=representation'});
const signup=(user,event)=>rest('rpc/register_for_event',user,'POST',{target_event:event});
const regRows=()=>JSON.parse(sql("select coalesce(json_agg(r order by id),'[]') from public.registrations r"));
const cleanup=async()=>{for(const u of users){const deleted=await rest('registrations?user_id=eq.'+u.id,u,'DELETE');assert.equal(deleted.status,200,'검증 신청 정리 실패');}};
const sqlError=(query,db,code)=>assert.throws(()=>sql(query,db),error=>String(error.stderr).includes(code+':'));
try {
 assert.equal((await rest('events',undefined)).status,401);
 assert.equal((await rest('registrations',undefined)).status,401);
 assert.equal((await signup(undefined,events[0])).status,401);
 assert.equal((await rest('events',a)).data.length,3); pass('비로그인 테이블/RPC 접근 거절 · 로그인 모임 3개 조회');
 const ra=await signup(a,events[0]); assert.equal(ra.status,200);assert.equal(ra.data.user_id,a.id);
 const rb=await signup(b,events[0]); assert.equal(rb.status,200);
 assert.equal((await rest('registrations',a)).data.length,1);
 assert.equal((await rest('registrations?id=eq.'+rb.data.id,a)).data.length,0);pass('A는 본인 신청만 조회 · B 신청은 0행');
 const forged=await rest('registrations',a,'POST',{event_id:events[2],user_id:b.id});
 assert.equal(forged.status,403);assert.equal(forged.data.code,'42501');pass('직접 API에 B ID를 넣은 A의 위조 신청 거절');
 const dup=await signup(a,events[0]);assert.equal(dup.status,409);assert.equal(dup.data.code,'23505');
 assert.equal(Number(sql(`select registered_count from public.events where id='${events[0]}'`)),2);pass('중복 신청 거절 · 실패한 INSERT의 정원 카운터도 rollback');
 const missing=await signup(a,'10000000-0000-4000-8000-000000000099');assert.equal(missing.status,409);assert.equal(missing.data.code,'23503');pass('없는 모임 신청 거절');
 const changed=await rest('registrations?id=eq.'+ra.data.id,a,'PATCH',{note:'복원해도 남아야 할 메모'});assert.equal(changed.status,200);assert.equal(changed.data[0].note,'복원해도 남아야 할 메모');
 const other=await rest('registrations?id=eq.'+rb.data.id,a,'PATCH',{note:'침범'});assert.equal(other.status,200);assert.deepEqual(other.data,[]);
 const otherDelete=await rest('registrations?id=eq.'+rb.data.id,a,'DELETE');assert.equal(otherDelete.status,200);assert.deepEqual(otherDelete.data,[]);
 assert.equal((await rest('registrations?id=eq.'+rb.data.id,b)).data.length,1);pass('본인 메모 수정 허용 · 타인 수정/삭제는 성공 HTTP라도 영향 0행');
 const owner=await rest('registrations?id=eq.'+ra.data.id,a,'PATCH',{user_id:b.id});assert.equal(owner.status,403);
 const move=await rest('registrations?id=eq.'+ra.data.id,a,'PATCH',{event_id:events[2]});assert.equal(move.status,403);
 const capacity=await rest('events?id=eq.'+events[0],a,'PATCH',{capacity:999});assert.equal(capacity.status,403);pass('신청 소유자/모임 이동 및 정원 직접 변경 권한 차단');
 const race=await Promise.all([signup(a,events[1]),signup(b,events[1])]);
 assert.deepEqual(race.map(r=>r.status).sort(),[200,400]);
 assert.equal(race.find(r=>r.status===400).data.code,'23514');
 assert.equal(Number(sql(`select count(*) from public.registrations where event_id='${events[1]}'`)),1);
 assert.equal(Number(sql(`select registered_count from public.events where id='${events[1]}'`)),1);pass('동시에 마지막 자리 신청: 1명 성공 · 1명 정원 오류 · 실제 1행');
 const before=Number(sql('select count(*) from public.registrations'));
 sqlError(`begin; insert into public.registrations(event_id,user_id) values ('${events[2]}','${a.id}'); select 1/0; commit;`,'postgres','22012');
 assert.equal(Number(sql('select count(*) from public.registrations')),before);
 assert.equal(Number(sql(`select registered_count from public.events where id='${events[2]}'`)),0);pass('신청 직후 강제 오류: 신청과 정원 갱신 함께 rollback');
 const dir=path.join(app,'.local');mkdirSync(dir,{recursive:true});
 // 계정도 포함한 연습용 논리 백업. 파일·클라우드 설정·WAL/PITR은 포함하지 않는다.
 const backup=run('docker',['exec',container,'pg_dump','-U','postgres','-d','postgres','--schema=public','--schema=auth']);
 const backupFile=path.join(dir,'practice-backup.sql');writeFileSync(backupFile,backup,{mode:0o600});
 const snapshot=regRows();
 for(const db of ['learnstead_migration_check','learnstead_restore_check']) {
   assert.equal(sql(`select count(*) from pg_database where datname='${db}'`).trim(),'0','이름이 같은 DB가 이미 있으면 보존하고 중단');
   sql(`create database ${db}`); created.push(db);
   sql('drop schema public cascade; create schema extensions;',db);
   sql(backup,db);
 }
 const migration=readFileSync(path.join(root,'supabase/migrations/20260913000200_registration_note.sql'),'utf8');
 sql('drop policy registrations_update on public.registrations; alter table public.registrations drop column note;', 'learnstead_migration_check');
 sql(migration,'learnstead_migration_check');
 const projected = rows => rows.map(({note,...row})=>row);
 const migrated=JSON.parse(sql("select coalesce(json_agg(r order by id),'[]') from public.registrations r",'learnstead_migration_check'));
 assert.deepEqual(projected(migrated),projected(snapshot));
 assert.equal(Number(sql("select count(*) from public.registrations where note=''",'learnstead_migration_check')),snapshot.length);pass('기존 신청이 있는 별도 DB에 메모 migration 적용 · 행 수/기본값 보존');
 // 실패 fixture: 백업 후 별도 복원 DB에서 한 행을 삭제하고 복원 전 차이를 확인한다.
 sql(`delete from public.registrations where id='${snapshot[0].id}'`,'learnstead_restore_check');
 assert.equal(Number(sql('select count(*) from public.registrations','learnstead_restore_check')),snapshot.length-1);pass('복원 실패 fixture: 신청 1행 삭제를 실제 관찰');
 sql('drop schema public cascade; drop schema auth cascade;','learnstead_restore_check');
 sql(backup,'learnstead_restore_check');
 const restored=JSON.parse(sql("select coalesce(json_agg(r order by id),'[]') from public.registrations r",'learnstead_restore_check'));
 assert.deepEqual(restored,snapshot);
 assert.equal(sql("select string_agg(id::text || ':' || registered_count::text,',' order by id) from public.events",'learnstead_restore_check'),sql("select string_agg(id::text || ':' || registered_count::text,',' order by id) from public.events"));
 const restoredRole = (u, query) => sql(`begin; set local role authenticated; set local request.jwt.claim.sub='${u.id}'; ${query}; rollback;`, 'learnstead_restore_check').trim().split('\n').filter(line=>!['BEGIN','SET','ROLLBACK'].includes(line));
 for (const u of users) {
   const expected=snapshot.filter(x=>x.user_id===u.id).map(x=>x.id).sort();
   assert.deepEqual(JSON.parse(restoredRole(u,"select coalesce(json_agg(id order by id),'[]') from public.registrations")[0]),expected);
   const foreign=snapshot.find(x=>x.user_id!==u.id);
   assert.deepEqual(restoredRole(u,`update public.registrations set note='침범' where id='${foreign.id}'; delete from public.registrations where id='${foreign.id}'`),['UPDATE 0','DELETE 0']);
   const own=snapshot.find(x=>x.user_id===u.id);
   assert.deepEqual(restoredRole(u,`update public.registrations set note='내 메모' where id='${own.id}'`),['UPDATE 1']);
 }
 sqlError('begin; set local role anon; select * from public.registrations; rollback;', 'learnstead_restore_check','42501');
 sqlError(`insert into public.registrations(event_id,user_id) values ('${events[0]}','${a.id}')`, 'learnstead_restore_check','23505');
 sqlError(`insert into public.registrations(event_id,user_id) values ('${events[2]}','00000000-0000-4000-8000-000000000099')`, 'learnstead_restore_check','23503');
 assert.deepEqual(JSON.parse(sql("select coalesce(json_agg(r order by id),'[]') from public.registrations r",'learnstead_restore_check')),snapshot);
 assert.equal(sql("select count(*) from pg_policies where schemaname='public'",'learnstead_restore_check').trim(),'5');
 assert.equal(sql("select has_column_privilege('authenticated','public.registrations','note','UPDATE')",'learnstead_restore_check').trim(),'t');
 pass('별도 DB에 논리 백업 복원 · 모든 값/정원/5개 RLS 정책/메모 권한 확인');
} finally {try{await cleanup();}finally{for(const db of created) sql(`drop database ${db}`);}}
assert.equal(Number(sql('select count(*) from public.registrations')),0);
assert.equal(Number(sql('select sum(registered_count) from public.events')),0);pass('본인 취소 허용 · 검증 신청 0개 및 정원 카운터 0 복귀');
const evidence={date:new Date().toISOString(),node:process.version,postgres:sql('show server_version').trim(),passed:results.length,results,limits:['macOS local Docker only','No Windows or hosted Supabase execution','Logical public/auth backup; no Storage files or PITR','Restored RLS checked with SQL role; live primary RLS checked via Auth and REST']};
writeFileSync(path.join(app,'.local/verification.json'),JSON.stringify(evidence,null,2));
console.log(`검증 완료: ${results.length}개 판정 PASS. .local/verification.json, .local/practice-backup.sql 저장.`);
