import http from 'node:http';
import {readFile} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
const allowed={'/':['index.html','text/html'],'/style.css':['style.css','text/css'],'/main.js':['main.js','text/javascript'],'/config.json':['.local/public-config.json','application/json']};
const server=http.createServer(async(req,res)=>{
 const route=allowed[new URL(req.url,'http://127.0.0.1').pathname];
 if(req.method!=='GET'||!route){res.writeHead(404);res.end('찾을 수 없습니다');return;}
 try{const body=await readFile(fileURLToPath(new URL(route[0],import.meta.url)));res.writeHead(200,{'Content-Type':route[1]+'; charset=utf-8','Cache-Control':'no-store','X-Content-Type-Options':'nosniff','Content-Security-Policy':"default-src 'self'; connect-src 'self' http://127.0.0.1:55321; style-src 'self'; script-src 'self'; frame-ancestors 'none'"});res.end(body);}
 catch{res.writeHead(503);res.end('앱 폴더에서 npm run setup을 먼저 실행하세요.');}
});
server.listen(5173,'127.0.0.1',()=>console.log('스터디 신청 연습: http://127.0.0.1:5173 (이 컴퓨터에서만 접근)'));
