import assert from 'node:assert/strict';
import {mkdirSync,writeFileSync,readFileSync} from 'node:fs';
import path from 'node:path';
import {status,setup,request,sql,run,app,root,container,password} from './local.mjs';
import {createObservations} from './observations.mjs';
const {observations,observe}=createObservations();
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
const sqlError=(query,db,code)=>{
 let observed;
 assert.throws(()=>sql(query,db),error=>{observed=String(error.stderr).match(/ERROR:\s+([0-9A-Z]{5}):/)?.[1];return observed===code;});
 return observed;
};
const learnerRows=rows=>rows.map(r=>({id:r.id,user:r.user_id===a.id?'A':'B',event_id:r.event_id,...('note' in r?{note:r.note}:{})}));
try {
 const anonymous=await rest('events',undefined);
 observe('04','비로그인 모임 조회 HTTP',401,anonymous.status);
 assert.equal((await rest('registrations',undefined)).status,401);
 assert.equal((await signup(undefined,events[0])).status,401);
 assert.equal((await rest('events',a)).data.length,3); pass('비로그인 테이블/RPC 접근 거절 · 로그인 모임 3개 조회');
 const ra=await signup(a,events[0]); assert.equal(ra.status,200);assert.equal(ra.data.user_id,a.id);
 const rb=await signup(b,events[0]); assert.equal(rb.status,200);
 const ownRows=(await rest('registrations',a)).data;
 observe('02','A의 첫 신청 후 A의 신청 수',1,ownRows.length);
 const hidden=await rest('registrations?id=eq.'+rb.data.id,a);
 observe('04','A가 B의 신청 조회',{http:200,returned:[],ownerRows:1},{http:hidden.status,returned:hidden.data,ownerRows:(await rest('registrations?id=eq.'+rb.data.id,b)).data.length});pass('A는 본인 신청만 조회 · B 신청은 0행');
 const forged=await rest('registrations',a,'POST',{event_id:events[2],user_id:b.id});
 observe('04','A가 B 소유로 신청 생성',{http:403,error:'42501',forgedRows:0},{http:forged.status,error:forged.data.code,forgedRows:regRows().filter(r=>r.user_id===b.id&&r.event_id===events[2]).length});pass('직접 API에 B ID를 넣은 A의 위조 신청 거절');
 const duplicateBefore=regRows().filter(r=>r.user_id===a.id&&r.event_id===events[0]).length;
 const dup=await signup(a,events[0]);assert.equal(dup.status,409);assert.equal(dup.data.code,'23505');
 observe('02','같은 신청 반복',{before:1,after:1,http:409,error:'23505',counter:2},{before:duplicateBefore,after:regRows().filter(r=>r.user_id===a.id&&r.event_id===events[0]).length,http:dup.status,error:dup.data.code,counter:Number(sql(`select registered_count from public.events where id='${events[0]}'`))});pass('중복 신청 거절 · 실패한 INSERT의 정원 카운터도 rollback');
 const missingBefore=regRows().length;
 const missing=await signup(a,'10000000-0000-4000-8000-000000000099');assert.equal(missing.status,409);assert.equal(missing.data.code,'23503');
 observe('02','없는 모임 신청',{http:409,error:'23503',before:missingBefore,after:missingBefore,invalidRows:0},{http:missing.status,error:missing.data.code,before:missingBefore,after:regRows().length,invalidRows:regRows().filter(r=>r.event_id==='10000000-0000-4000-8000-000000000099').length});pass('없는 모임 신청 거절');
 const changed=await rest('registrations?id=eq.'+ra.data.id,a,'PATCH',{note:'복원해도 남아야 할 메모'});assert.equal(changed.status,200);assert.equal(changed.data[0].note,'복원해도 남아야 할 메모');
 const bBefore=(await rest('registrations?id=eq.'+rb.data.id,b)).data;
 const other=await rest('registrations?id=eq.'+rb.data.id,a,'PATCH',{note:'침범'});assert.equal(other.status,200);assert.deepEqual(other.data,[]);
 observe('04','A가 B의 메모 수정',{http:200,returned:[],owner:learnerRows(bBefore)},{http:other.status,returned:other.data,owner:learnerRows((await rest('registrations?id=eq.'+rb.data.id,b)).data)});
 const otherDelete=await rest('registrations?id=eq.'+rb.data.id,a,'DELETE');assert.equal(otherDelete.status,200);assert.deepEqual(otherDelete.data,[]);
 observe('04','A가 B의 신청 삭제',{http:200,returned:[],owner:learnerRows(bBefore)},{http:otherDelete.status,returned:otherDelete.data,owner:learnerRows((await rest('registrations?id=eq.'+rb.data.id,b)).data)});
 observe('04','본인 메모 수정',{http:200,note:'복원해도 남아야 할 메모'},{http:changed.status,note:changed.data[0].note});pass('본인 메모 수정 허용 · 타인 수정/삭제는 성공 HTTP라도 영향 0행');
 const owner=await rest('registrations?id=eq.'+ra.data.id,a,'PATCH',{user_id:b.id});assert.equal(owner.status,403);
 const move=await rest('registrations?id=eq.'+ra.data.id,a,'PATCH',{event_id:events[2]});assert.equal(move.status,403);
 const capacity=await rest('events?id=eq.'+events[0],a,'PATCH',{capacity:999});assert.equal(capacity.status,403);
 observe('04','소유자·모임·정원 직접 변경 HTTP',{ownerChangeHttp:403,eventChangeHttp:403,capacityChangeHttp:403},{ownerChangeHttp:owner.status,eventChangeHttp:move.status,capacityChangeHttp:capacity.status});pass('신청 소유자/모임 이동 및 정원 직접 변경 권한 차단');
 const race=await Promise.all([signup(a,events[1]),signup(b,events[1])]);
 assert.deepEqual(race.map(r=>r.status).sort(),[200,400]);
 assert.equal(race.find(r=>r.status===400).data.code,'23514');
 assert.equal(Number(sql(`select count(*) from public.registrations where event_id='${events[1]}'`)),1);
 const raceRows=regRows().filter(r=>r.event_id===events[1]);
 const winner=race.findIndex(r=>r.status===200);
 observe('03','마지막 자리 동시 신청',{success:1,failure:1,rows:1,counter:1,owner:winner===0?'A':'B'},{success:race.filter(r=>r.status===200).length,failure:race.filter(r=>r.status!==200).length,rows:raceRows.length,counter:Number(sql(`select registered_count from public.events where id='${events[1]}'`)),owner:raceRows[0].user_id===a.id?'A':'B'});pass('동시에 마지막 자리 신청: 1명 성공 · 1명 정원 오류 · 실제 1행');
 const before=Number(sql('select count(*) from public.registrations'));
 const rollbackCode=sqlError(`begin; insert into public.registrations(event_id,user_id) values ('${events[2]}','${a.id}'); select 1/0; commit;`,'postgres','22012');
 assert.equal(Number(sql('select count(*) from public.registrations')),before);
 observe('03','강제 오류 전후',{before,after:before,error:'22012',remainingChanges:0,counter:0},{before,after:regRows().length,error:rollbackCode,remainingChanges:regRows().length-before,counter:Number(sql(`select registered_count from public.events where id='${events[2]}'`))});pass('신청 직후 강제 오류: 신청과 정원 갱신 함께 rollback');
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
 const migrationBefore=JSON.parse(sql("select coalesce(json_agg(r order by id),'[]') from public.registrations r",'learnstead_migration_check'));
 sql(migration,'learnstead_migration_check');
 const projected = rows => rows.map(({note,...row})=>row);
 const migrated=JSON.parse(sql("select coalesce(json_agg(r order by id),'[]') from public.registrations r",'learnstead_migration_check'));
 assert.deepEqual(projected(migrated),projected(snapshot));
 observe('05','메모 열 추가 전후 신청',{before:learnerRows(snapshot).map(({note,...r})=>r),after:learnerRows(snapshot).map(r=>({...r,note:''}))},{before:learnerRows(migrationBefore),after:learnerRows(migrated)});
 observe('05','행 수와 기본값',{before:snapshot.length,after:snapshot.length,emptyNotes:snapshot.length},{before:migrationBefore.length,after:migrated.length,emptyNotes:Number(sql("select count(*) from public.registrations where note=''",'learnstead_migration_check'))});pass('기존 신청이 있는 별도 DB에 메모 migration 적용 · 행 수/기본값 보존');
 // 실패 fixture: 백업 후 별도 복원 DB에서 한 행을 삭제하고 복원 전 차이를 확인한다.
 sql(`delete from public.registrations where id='${snapshot[0].id}'`,'learnstead_restore_check');
 observe('06','복원 전 한 행 삭제',{before:snapshot.length,after:snapshot.length-1},{before:snapshot.length,after:Number(sql('select count(*) from public.registrations','learnstead_restore_check'))});pass('복원 실패 fixture: 신청 1행 삭제를 실제 관찰');
 sql('drop schema public cascade; drop schema auth cascade;','learnstead_restore_check');
 sql(backup,'learnstead_restore_check');
 const restored=JSON.parse(sql("select coalesce(json_agg(r order by id),'[]') from public.registrations r",'learnstead_restore_check'));
 assert.deepEqual(restored,snapshot);
 observe('06','백업 기준과 복원본 신청',learnerRows(snapshot),learnerRows(restored));
 const eventCount=Number(sql('select count(*) from public.events'));
 observe('06','모임·신청 행 수',{events:eventCount,registrations:snapshot.length},{events:Number(sql('select count(*) from public.events','learnstead_restore_check')),registrations:restored.length});
 assert.equal(sql("select string_agg(id::text || ':' || registered_count::text,',' order by id) from public.events",'learnstead_restore_check'),sql("select string_agg(id::text || ':' || registered_count::text,',' order by id) from public.events"));
 const restoredRole = (u, query) => sql(`begin; set local role authenticated; set local request.jwt.claim.sub='${u.id}'; ${query}; rollback;`, 'learnstead_restore_check').trim().split('\n').filter(line=>!['BEGIN','SET','ROLLBACK'].includes(line));
 for (const u of users) {
   const expected=snapshot.filter(x=>x.user_id===u.id).map(x=>x.id).sort();
   observe('06',`${u===a?'A':'B'} 역할의 신청 ID 조회`,expected,JSON.parse(restoredRole(u,"select coalesce(json_agg(id order by id),'[]') from public.registrations")[0]));
   const foreign=snapshot.find(x=>x.user_id!==u.id);
   observe('06',`${u===a?'A':'B'} 역할의 타인 수정·삭제`,['UPDATE 0','DELETE 0'],restoredRole(u,`update public.registrations set note='침범' where id='${foreign.id}'; delete from public.registrations where id='${foreign.id}'`));
   const own=snapshot.find(x=>x.user_id===u.id);
   observe('06',`${u===a?'A':'B'} 역할의 본인 메모 수정`,['UPDATE 1'],restoredRole(u,`update public.registrations set note='내 메모' where id='${own.id}'`));
 }
 observe('06','비로그인 역할 조회 오류','42501',sqlError('begin; set local role anon; select * from public.registrations; rollback;', 'learnstead_restore_check','42501'));
 observe('06','복원본 중복 신청 오류','23505',sqlError(`insert into public.registrations(event_id,user_id) values ('${events[0]}','${a.id}')`, 'learnstead_restore_check','23505'));
 observe('06','복원본 없는 사용자 연결 오류','23503',sqlError(`insert into public.registrations(event_id,user_id) values ('${events[2]}','00000000-0000-4000-8000-000000000099')`, 'learnstead_restore_check','23503'));
 assert.deepEqual(JSON.parse(sql("select coalesce(json_agg(r order by id),'[]') from public.registrations r",'learnstead_restore_check')),snapshot);
 assert.equal(sql("select count(*) from pg_policies where schemaname='public'",'learnstead_restore_check').trim(),'5');
 assert.equal(sql("select has_column_privilege('authenticated','public.registrations','note','UPDATE')",'learnstead_restore_check').trim(),'t');
 pass('별도 DB에 논리 백업 복원 · 모든 값/정원/5개 RLS 정책/메모 권한 확인');
} finally {try{await cleanup();}finally{for(const db of created) sql(`drop database ${db}`);}}
assert.equal(Number(sql('select count(*) from public.registrations')),0);
observe('정리','검증 종료 후 신청·카운터',{rows:0,counter:0},{rows:Number(sql('select count(*) from public.registrations')),counter:Number(sql('select sum(registered_count) from public.events'))});pass('본인 취소 허용 · 검증 신청 0개 및 정원 카운터 0 복귀');
const evidence={date:new Date().toISOString(),node:process.version,postgres:sql('show server_version').trim(),passed:results.length,results,observations,limits:['macOS local Docker only','No Windows or hosted Supabase execution','Logical public/auth backup; no Storage files or PITR','Restored RLS checked with SQL role; live primary RLS checked via Auth and REST']};
writeFileSync(path.join(app,'.local/verification.json'),JSON.stringify(evidence,null,2));
console.log(`검증 완료: ${results.length}개 판정 PASS. .local/verification.json, .local/practice-backup.sql 저장.`);
