// 모의 Docker 서버로 전달기의 실제 HTTP 경로를 검증한다. 실제 Docker 변경은 없다.
import http from 'node:http';
import assert from 'node:assert/strict';
import {mkdtempSync,writeFileSync,rmSync,existsSync} from 'node:fs';
import {tmpdir} from 'node:os';
import path from 'node:path';
import {startLoopback} from './loopback-start.mjs';
const directory=mkdtempSync(path.join(process.platform==='darwin'?'/tmp':tmpdir(),'learnstead-proxy-test-'));
const socket=path.join(directory,'mock.sock');
const received=[];let proxySocket;let waiting;
const mock=http.createServer(async(req,res)=>{
 const chunks=[];for await(const part of req)chunks.push(part);
 const raw=Buffer.concat(chunks).toString();received.push({method:req.method,url:req.url,body:raw?JSON.parse(raw):null});
 res.setHeader('Content-Type','application/json');
 if(req.url==='/containers/own-container/wait'){res.writeHead(200);res.flushHeaders();waiting=res;return;}
 if(req.url==='/containers/own-container/start'&&waiting){waiting.end('{}');waiting=undefined;}
 if(req.url==='/containers/foreign/json')res.end(JSON.stringify({Config:{Labels:{'com.supabase.cli.project':'other-project'}}}));
 else if(req.url==='/volumes/owned')res.end(JSON.stringify({Labels:{'com.supabase.cli.project':'learnstead-db-guide'}}));
 else if(req.url==='/volumes/foreign')res.end(JSON.stringify({Labels:{'com.supabase.cli.project':'other-project'}}));
 else if(req.url.startsWith('/proxy-socket?')){proxySocket=new URL(req.url,'http://mock').searchParams.get('path');res.end('{}');}
 else if(req.url==='/containers/own-container/exec')res.end(JSON.stringify({Id:JSON.parse(raw).mode==='200'?'owned-exec200':'owned-exec'}));
 else if(req.url.startsWith('/containers/create'))res.end('{"Id":"own-container"}');
 else res.end('{}');
});
mock.on('upgrade',(req,stream,head)=>{
 assert(['/exec/owned-exec/start','/exec/owned-exec200/start','/containers/own-container/attach'].includes(req.url));
 assert.equal(head.toString(),'{}','HTTP head의 요청 본문이 보존되어야 함');
 const legacy=req.url.includes('exec200');
 stream.write(legacy?'HTTP/1.1 200 OK\r\nConnection: close\r\n\r\n':'HTTP/1.1 101 UPGRADED\r\nConnection: Upgrade\r\nUpgrade: tcp\r\n\r\n');
 stream.end('fixture-output');
});
await new Promise(resolve=>mock.listen(socket,resolve));
const child=path.join(directory,'client.mjs');
writeFileSync(child,`
import http from 'node:http';import assert from 'node:assert/strict';
const socket=process.env.DOCKER_HOST.slice(7);
const req=(url,body,method='POST')=>new Promise((resolve,reject)=>{const r=http.request({socketPath:socket,path:url,method,headers:{'Content-Type':'application/json'}},s=>{s.resume();s.on('end',()=>resolve(s.statusCode));});r.on('error',reject);r.end(body===undefined?undefined:JSON.stringify(body));});
assert.equal(await req('/proxy-socket?path='+encodeURIComponent(socket),undefined,'GET'),200);
assert.equal(await req('/containers/create?name=foreign',{Labels:{'com.supabase.cli.project':'other-project'}}),403);
assert.equal(await req('/containers/foreign/stop',{}),403);
assert.equal(await req('/networks/prune',{}),403);
assert.equal(await req('/containers/prune?filters='+encodeURIComponent(JSON.stringify({label:['com.supabase.cli.project=learnstead-db-guide','com.supabase.cli.project=foreign']})),{}),403);
assert.equal(await req('/volumes/foreign',undefined,'DELETE'),403);
assert.equal(await req('/containers/prune?filters='+encodeURIComponent(JSON.stringify({label:{'com.supabase.cli.project=learnstead-db-guide':false}})),{}),403);
assert.equal(await req('/volumes/create',{Name:'unrelated'}),403);
assert.equal(await req('/images/create?fromImage=untrusted/image',{}),403);
assert.equal(await req('/containers/create?name=supabase_test_learnstead-db-guide',{Labels:{'com.supabase.cli.project':'learnstead-db-guide'},HostConfig:{PortBindings:{'5432/tcp':[{HostIp:'0.0.0.0',HostPort:'55322'}]}}}),200);
await new Promise((resolve,reject)=>{const r=http.request({socketPath:socket,path:'/containers/own-container/wait',method:'POST'},response=>{r.setTimeout(0);response.resume();resolve();});r.setTimeout(2000,()=>r.destroy(new Error('wait headers delayed')));r.on('error',reject);r.end();});
assert.equal(await req('/containers/own-container/start',{}),200);
assert.equal(await req('/containers/own-container/exec',{}),200);
assert.equal(await req('/containers/own-container/exec',{mode:'200'}),200);
const upgrade=(id,attach=false)=>new Promise((resolve,reject)=>{const r=http.request({socketPath:socket,path:attach?'/containers/'+id+'/attach':'/exec/'+id+'/start',method:'POST',headers:{Connection:'Upgrade',Upgrade:'tcp','Content-Length':'2'}},response=>{let data='';response.on('data',chunk=>data+=chunk);response.on('end',()=>resolve(response.statusCode===403?'403':data));});r.on('upgrade',(response,stream,head)=>{let data=head.toString();stream.on('data',chunk=>data+=chunk);stream.on('end',()=>resolve(data));});r.on('error',reject);r.end('{}');});
assert.equal(await upgrade('foreign-exec'),'403');
assert.equal(await upgrade('owned-exec'),'fixture-output');
assert.equal(await upgrade('owned-exec200'),'fixture-output');
assert.equal(await upgrade('foreign',true),'403');
assert.equal(await upgrade('own-container',true),'fixture-output');
assert.equal(await req('/volumes/owned',undefined,'DELETE'),200);
assert.equal(await req('/containers/prune?filters='+encodeURIComponent(JSON.stringify({label:['com.supabase.cli.project=learnstead-db-guide']})),{}),200);
`);
const previous=process.env.DOCKER_HOST;process.env.DOCKER_HOST='unix://'+socket;
try {
 await startLoopback(process.execPath,[child],'learnstead-db-guide',directory);
 const mutations=received.filter(x=>x.method==='POST');assert.equal(mutations.length,6);
 assert.equal(mutations[0].body.HostConfig.PortBindings['5432/tcp'][0].HostIp,'127.0.0.1');
 assert(!existsSync(proxySocket));
 console.log('PASS 전달기: 다른 프로젝트/전역 변경 8종 거절 · 소유 컨테이너만 전달 · loopback 강제 · own exec/attach 101/200 및 head 보존 · wait 헤더 즉시 전달 · 소켓 정리');
} finally {
 if(previous===undefined)delete process.env.DOCKER_HOST;else process.env.DOCKER_HOST=previous;
 mock.closeAllConnections();await new Promise(resolve=>mock.close(resolve));rmSync(directory,{recursive:true,force:true});
}
