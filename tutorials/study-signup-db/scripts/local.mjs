import {startLoopback} from './loopback-start.mjs';
import {execFileSync} from 'node:child_process';
import {mkdirSync, writeFileSync, readFileSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
if(Number(process.versions.node.split('.')[0])!==24)throw new Error('이 실습은 Node.js 24 LTS를 사용합니다. node --version을 확인하세요.');
export const root = fileURLToPath(new URL('../', import.meta.url));
export const app = path.join(root, 'app');
export const project = 'learnstead-db-guide';
export const network = 'supabase_network_learnstead-db-guide';
export const container = 'supabase_db_' + project;
export const password = 'Learnstead-local-2026!';
export const run = (command, args, options = {}) => execFileSync(command, args, {cwd: app, encoding:'utf8', ...options});
export const cli = (...args) => run(path.join(app, 'node_modules/.bin/supabase' + (process.platform === 'win32' ? '.cmd' : '')), [...args, '--workdir', root], {env:{...process.env, SUPABASE_TELEMETRY_DISABLED:'1'}});
export function status() {
  const data = JSON.parse(cli('status','-o','json'));
  if (data.API_URL !== 'http://127.0.0.1:55321') throw new Error('연습용 로컬 API 주소가 아닙니다. 중단합니다.');
  return data;
}
export function sql(query, database = 'postgres') {
  if (!['postgres','learnstead_migration_check','learnstead_restore_check'].includes(database)) throw new Error('허용하지 않은 DB');
  return run('docker',['exec','-i',container,'psql','-X','-U',database === 'postgres' ? 'postgres' : 'supabase_admin','-d',database,'-v','ON_ERROR_STOP=1','-v','VERBOSITY=verbose','-At'],{input:query});
}
export async function request(config, endpoint, {token, method='GET', body, admin=false, prefer} = {}) {
  const key = admin ? config.SERVICE_ROLE_KEY : config.ANON_KEY;
  const response = await fetch(config.API_URL + endpoint, {method, headers:{apikey:key,Authorization:`Bearer ${token || key}`,'Content-Type':'application/json',...(prefer ? {Prefer:prefer} : {})},body:body === undefined ? undefined : JSON.stringify(body)});
  const raw = await response.text();
  return {status:response.status, ok:response.ok, data:raw ? JSON.parse(raw) : null};
}
export async function setup(config) {
  const found = await request(config,'/auth/v1/admin/users',{admin:true});
  if (!found.ok) throw new Error('연습 계정 목록 확인 실패');
  for (const name of ['alice','bob']) {
    const email = name + '@example.com';
    const user = found.data.users.find(u=>u.email === email);
    const result = await request(config,'/auth/v1/admin/users' + (user ? '/' + user.id : ''), {admin:true,method:user?'PUT':'POST',body:{email,password,email_confirm:true}});
    if (!result.ok) throw new Error('연습 계정 생성 실패: '+JSON.stringify(result.data));
  }
  mkdirSync(path.join(app,'.local'),{recursive:true});
  writeFileSync(path.join(app,'.local/public-config.json'),JSON.stringify({url:config.API_URL,anonKey:config.ANON_KEY}));
  console.log('PASS 연습 계정 2개 준비 · 앱용 공개 설정 생성 (기존 신청 내역 보존)');
}
export function verifyBindings() {
    const names = run('docker',['ps','--filter','label=com.supabase.cli.project='+project,'--format','{{.Names}}']).trim().split('\n').filter(Boolean);
    if(!names.includes(container)||!names.includes('supabase_kong_'+project))throw new Error('필수 연습 컨테이너가 없습니다.');
    for (const name of names) {
      const ports=JSON.parse(run('docker',['inspect',name]))[0].NetworkSettings.Ports;
      for(const bindings of Object.values(ports||{})) for(const binding of bindings||[]) if(binding.HostIp !== '127.0.0.1' && binding.HostIp !== '::1') {
        console.error(name, JSON.stringify(ports)); cli('stop'); throw new Error('loopback 외부 바인딩을 발견하여 이 실습을 중지했습니다.');
      }
    }
}
export async function startLocal() {
    let net;
    try { net=JSON.parse(run('docker',['network','inspect',network],{stdio:['ignore','pipe','pipe']}))[0]; } catch {run('docker',['network','create','--label','learnstead.local=true','--opt','com.docker.network.bridge.host_binding_ipv4=127.0.0.1',network]);}
    if (net && (net.Labels?.['learnstead.local'] !== 'true' || net.Options?.['com.docker.network.bridge.host_binding_ipv4'] !== '127.0.0.1')) throw new Error('기존 network의 loopback 설정이 다릅니다. 자동 변경하지 않습니다.');
    for(const type of ['container','volume']) {
      const names=run('docker',type==='container'?['ps','-a','--format','{{.Names}}']:['volume','ls','--format','{{.Name}}']).trim().split('\n').filter(name=>name.startsWith('supabase_')&&name.endsWith('_'+project));
      for(const name of names){const info=JSON.parse(run('docker',[type,'inspect',name]))[0];const labels=type==='container'?info.Config.Labels:info.Labels;if(labels?.['com.supabase.cli.project']!==project)throw new Error('같은 이름의 다른 프로젝트 리소스를 발견했습니다. 보존하고 중단합니다.');}
    }
    console.log('로컬 컨테이너 준비 중입니다. 첫 실행은 이미지 다운로드로 오래 걸릴 수 있습니다.');
    await startLoopback(path.join(app,'node_modules/.bin/supabase'), ['start','--network-id',network,'--workdir',root], project, app);
    verifyBindings();
    console.log('PASS 로컬 Supabase 시작 · API http://127.0.0.1:55321 · Studio http://127.0.0.1:55323');
}
async function main() {
  const action = process.argv[2];
  if (action === 'start') await startLocal();
  else if (action === 'setup') await setup(status());
  else if (action === 'stop') {cli('stop'); console.log('연습용 Supabase 중지. 로컬 볼륨 데이터는 보존됩니다.');}
  else if (action === 'reset' && process.argv.includes('--confirm-local-reset')) {
    status();
    const volume='supabase_db_'+project;
    const info=JSON.parse(run('docker',['volume','inspect',volume]))[0];
    if(info.Name!==volume || info.Labels?.['com.supabase.cli.project']!==project)throw new Error('연습 DB 볼륨 소유권이 다릅니다. 보존하고 중단합니다.');
    cli('stop');
    // --force 없이 정확히 이 DB 볼륨 하나만 제거한다. 사용 중이면 Docker가 거절한다.
    run('docker',['volume','rm',volume]);
    await startLocal();
    await setup(status());
    console.log('연습 DB 초기화 완료: 이벤트 3개, 신청 0개');
  }
  else throw new Error('start | setup | stop | reset --confirm-local-reset 중 선택하세요. reset은 이 연습 DB의 사용자·신청 데이터를 지웁니다.');
}
if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) main().catch(e=>{console.error(e.message);process.exitCode=1;});
