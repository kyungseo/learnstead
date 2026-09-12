// Docker Desktop에서 network 기본 바인딩이 무시될 때도 개별 포트에 loopback을 명시한다.
// 이 프록시는 시작 명령 동안에만 살아 있는 로컬 Unix socket이다.
import http from 'node:http';
import net from 'node:net';
import {spawn,execFileSync} from 'node:child_process';
import {mkdtempSync,rmSync,writeFileSync,mkdirSync} from 'node:fs';
import {tmpdir} from 'node:os';
import path from 'node:path';
export async function startLoopback(binary,args,project,cwd) {
 const context=JSON.parse(execFileSync('docker',['context','inspect'],{encoding:'utf8'}))[0];
 const daemon=process.env.DOCKER_HOST||context.Endpoints.docker.Host;
 if(!daemon.startsWith('unix://')) throw new Error('이 로컬 실행기는 Unix Docker socket 환경을 지원합니다. 원격 Docker와 Windows 네이티브 socket은 이 자료의 검증 범위 밖입니다.');
 const directory=mkdtempSync(path.join(process.platform==='darwin'?'/tmp':tmpdir(),'learnstead-db-'));
 const socket=path.join(directory,'docker.sock');
 let rewritten=0;
 let child;
 const streams=new Set();
 const closeStreams=()=>{for(const stream of streams)stream.destroy();};
 const cleanupSocket=()=>rmSync(directory,{recursive:true,force:true});
 const killGroup=signal=>{if(child?.pid)try{process.kill(-child.pid,signal);}catch{}};
 const interrupted=()=>{killGroup('SIGTERM');closeStreams();proxy.closeAllConnections();proxy.close();cleanupSocket();setTimeout(()=>{killGroup('SIGKILL');process.exit(130);},1000);};
 const ownContainers=new Set();
 const ownExecs=new Set();
 const daemonJSON=(url)=>new Promise((resolve,reject)=>{
  const request=http.get({socketPath:daemon.slice(7),path:url},response=>{let data='';response.on('data',chunk=>data+=chunk);response.on('end',()=>{try{resolve(JSON.parse(data));}catch(error){reject(error);}});});request.on('error',reject);
 });
 const isOwn=async(id)=>{
  if(ownContainers.has(id))return true;
  const info=await daemonJSON('/containers/'+encodeURIComponent(id)+'/json');
  if(info.Config?.Labels?.['com.supabase.cli.project']===project){ownContainers.add(id);return true;}
  return false;
 };
 const proxy=http.createServer(async(req,res)=>{
  try {
   const chunks=[];let size=0;for await(const chunk of req){size+=chunk.length;if(size>4*1024*1024){res.writeHead(413);res.end('요청 크기 제한');return;}chunks.push(chunk);}
   let body=Buffer.concat(chunks);
   const target=new URL(req.url,'http://docker.local');
   const endpoint=target.pathname.replace(/^\/v[0-9.]+/,'');
   if(!['GET','HEAD'].includes(req.method)) {
    let allowed=false;
    const item=endpoint.match(/^\/containers\/([^/]+)(?:\/(.*))?$/);
    if(endpoint==='/containers/create' && req.method==='POST') allowed=JSON.parse(body).Labels?.['com.supabase.cli.project']===project;
    else if(item && ((req.method==='DELETE'&&!item[2]) || (req.method==='POST'&&['start','stop','kill','restart','wait','exec','attach','resize'].includes(item[2])) || (req.method==='PUT'&&item[2]==='archive'))) allowed=await isOwn(item[1]);
    else if(endpoint==='/images/create' && req.method==='POST') allowed=target.searchParams.get('fromImage')?.startsWith('public.ecr.aws/supabase/')===true;
    else if(endpoint==='/networks/create' && req.method==='POST') allowed=JSON.parse(body).Name==='supabase_network_'+project;
    else if(/^\/volumes\/[^/]+$/.test(endpoint) && req.method==='DELETE') {const info=await daemonJSON(endpoint);allowed=info.Labels?.['com.supabase.cli.project']===project;}
    else if(endpoint==='/volumes/create' && req.method==='POST') {const name=JSON.parse(body).Name;allowed=typeof name==='string' && name.startsWith('supabase_') && name.endsWith('_'+project);}
    else if(['/containers/prune','/networks/prune','/volumes/prune'].includes(endpoint) && req.method==='POST') {
      const filters=JSON.parse(target.searchParams.get('filters')||'{}');
      const labels=Array.isArray(filters.label)?filters.label:Object.entries(filters.label||{}).filter(([,value])=>value===true).map(([key])=>key);
      allowed=labels.length===1&&labels[0]==='com.supabase.cli.project='+project;
    }
    else if(/^\/exec\/[^/]+\/start$/.test(endpoint)) allowed=ownExecs.has(endpoint.split('/')[2]);
    if(!allowed){console.error('학습 범위 외 Docker 요청 차단:',req.method,endpoint);res.writeHead(403);res.end('연습 프로젝트 범위 밖의 Docker 변경 거절');return;}
   }
   if(req.method==='POST' && /\/containers\/create(?:\?|$)/.test(req.url)) {
     const spec=JSON.parse(body);
     if(spec.Labels?.['com.supabase.cli.project']!==project){res.writeHead(403);res.end('이 연습 프로젝트 외 컨테이너 생성 거절');return;}
     for(const bindings of Object.values(spec.HostConfig?.PortBindings||{}))
       for(const binding of bindings||[]) {binding.HostIp='127.0.0.1';rewritten++;}
     body=Buffer.from(JSON.stringify(spec));
   }
   const headers={...req.headers,'content-length':String(body.length)};delete headers['transfer-encoding'];
   const upstream=http.request({socketPath:daemon.slice(7),path:req.url,method:req.method,headers},response=>{
    const track=endpoint==='/containers/create'||/^\/containers\/[^/]+\/exec$/.test(endpoint);
    if(track){let data='';response.on('data',chunk=>data+=chunk);response.on('end',()=>{try{const id=JSON.parse(data).Id;if(id)(endpoint==='/containers/create'?ownContainers:ownExecs).add(id);}catch{}res.writeHead(response.statusCode,response.headers);res.end(data);});}
    else {res.writeHead(response.statusCode,response.headers);res.flushHeaders();response.pipe(res);}
   });
   upstream.on('error',()=>{if(!res.headersSent)res.writeHead(502);res.end('Docker 연결 실패');});
   req.on('aborted',()=>upstream.destroy());upstream.end(body);
  } catch(error){if(!res.headersSent)res.writeHead(500);res.end(error.message);}
 });
 // 새 DB 초기화의 exec/attach만: 이 프로젝트의 컨테이너 소유권을 확인한다.
 proxy.on('upgrade',async(req,client,head)=>{
  client.pause();client.allowHalfOpen=true;
  const endpoint=new URL(req.url,'http://docker.local').pathname.replace(/^\/v[0-9.]+/,'');
  const match=endpoint.match(/^\/exec\/([^/]+)\/start$/);
  const attached=endpoint.match(/^\/containers\/([^/]+)\/attach$/);
  let owned=false;try{owned=match?ownExecs.has(match[1]):!!attached&&await isOwn(attached[1]);}catch{client.destroy();return;}
  const length=Number(req.headers['content-length']||0);
  if(req.method!=='POST'||!owned||req.headers['transfer-encoding']||!Number.isInteger(length)||length<0||length>4194304){console.error('학습 범위 외 Docker upgrade 차단:',endpoint);client.end('HTTP/1.1 403 Forbidden\r\nConnection: close\r\n\r\n');return;}
  client.pause();streams.add(client);
  const remote=net.connect({path:daemon.slice(7),allowHalfOpen:true});streams.add(remote);
  remote.once('connect',()=>{
   // Docker는 버전에 따라 101 또는 200으로 hijack한다. HTTP bytes와 head를 그대로 유지한다.
   remote.write(req.method+' '+req.url+' HTTP/'+req.httpVersion+'\r\n'+Object.entries(req.headers).map(([key,value])=>key+': '+value).join('\r\n')+'\r\n\r\n');
   if(head.length)remote.write(head);
   client.pipe(remote);remote.pipe(client);client.resume();
  });
  client.on('error',()=>remote.destroy());remote.on('error',()=>client.destroy());
  client.on('close',()=>{streams.delete(client);remote.destroy();});
  remote.on('close',()=>{streams.delete(remote);client.destroy();});
 });
 process.once('SIGINT',interrupted);process.once('SIGTERM',interrupted);
 try {
   await new Promise((resolve,reject)=>{proxy.once('error',reject);proxy.listen(socket,resolve);});
   await new Promise((resolve,reject)=>{
     child=spawn(binary,args,{cwd,detached:true,env:{...process.env,DOCKER_HOST:'unix://'+socket,SUPABASE_TELEMETRY_DISABLED:'1'},stdio:['ignore','pipe','pipe']});
     // CLI의 시작 stdout에는 관리자 키가 있다. 호출자나 브라우저에 전달하지 않는다.
     let output='';child.stdout.on('data',data=>{if(output.length<524288)output+=data;});child.stderr.on('data',data=>process.stderr.write(data));
     child.once('error',reject);child.once('exit',code=>{if(code===0)resolve();else{mkdirSync(path.join(cwd,'.local'),{recursive:true});writeFileSync(path.join(cwd,'.local/cli-failure.log'),output,{mode:0o600});reject(new Error('로컬 Supabase 명령 실패: '+code+' (.local/cli-failure.log 확인)'));}});
   });
   console.log(`로컬 포트 ${rewritten}개에 127.0.0.1 명시`);
 } finally {killGroup('SIGTERM');process.removeListener('SIGINT',interrupted);process.removeListener('SIGTERM',interrupted);closeStreams();proxy.closeAllConnections();await new Promise(resolve=>proxy.close(resolve));cleanupSocket();}
}
