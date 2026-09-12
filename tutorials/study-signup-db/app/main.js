const $=id=>document.getElementById(id);
let config,session=null;
function message(text,error=false){$('message').textContent=text;$('message').classList.toggle('error',error);}
function node(tag,text,className){const element=document.createElement(tag);if(text!==undefined)element.textContent=text;if(className)element.className=className;return element;}
async function api(endpoint,method='GET',body){
 const response=await fetch(config.url+endpoint,{method,headers:{apikey:config.anonKey,Authorization:'Bearer '+(session?.access_token||config.anonKey),'Content-Type':'application/json',Prefer:'return=representation'},body:body===undefined?undefined:JSON.stringify(body)});
 const raw=await response.text();const data=raw?JSON.parse(raw):null;
 if(!response.ok){const code=data?.code;throw new Error(code==='23505'?'이미 신청한 모임입니다.':code==='23514'?'정원이 찼거나 입력값이 허용 범위를 벗어났습니다.':response.status===401?'로그인 시간이 지났습니다. 다시 로그인해 주세요.':data?.message||data?.error_description||'요청을 처리하지 못했습니다.');}return data;
}
function authView(){const logged=!!session;$('login').hidden=logged;$('logout').hidden=!logged;$('refresh').hidden=!logged;$('identity').textContent=logged?session.user.email+' 계정으로 확인 중입니다.':'로그인하면 모임과 내 신청 내역이 나타납니다.';}
async function action(button,work){button.disabled=true;try{await work();}catch(e){message(e.message,true);}finally{button.disabled=false;}}
async function load(){
 const [events,registrations]=await Promise.all([api('/rest/v1/events?order=id'),api('/rest/v1/registrations?order=created_at')]);
 $('events').replaceChildren();$('registrations').replaceChildren();
 events.forEach((event,i)=>{const card=node('article',undefined,'card');card.append(node('span',String(i+1).padStart(2,'0'),'number'),node('h3',event.title),node('p',`${event.registered_count}명 신청 · 정원 ${event.capacity}명`,'seats'));const own=registrations.some(r=>r.event_id===event.id);const button=node('button',own?'신청 완료':'모임 신청');button.disabled=own;button.addEventListener('click',()=>action(button,async()=>{await api('/rest/v1/rpc/register_for_event','POST',{target_event:event.id});await load();message('신청을 저장했습니다. 다른 계정에서도 확인해 보세요.');}));card.append(button);$('events').append(card);});
 if(!registrations.length)$('registrations').append(node('p','신청 내역이 없습니다. 원하는 모임에 신청해 보세요.','empty'));
 for(const reg of registrations){const item=node('article',undefined,'registration');item.append(node('h3',events.find(e=>e.id===reg.event_id)?.title||'모임'));const form=node('form');const label=node('label','내 메모 (최대 200자)');const input=node('input');input.value=reg.note;input.maxLength=200;label.append(input);const save=node('button','메모 저장','secondary');const cancel=node('button','신청 취소','danger');cancel.type='button';form.append(label,save,cancel);form.addEventListener('submit',e=>{e.preventDefault();action(save,async()=>{const changed=await api('/rest/v1/registrations?id=eq.'+reg.id,'PATCH',{note:input.value});if(changed.length!==1)throw new Error('변경된 신청이 없습니다. 새로 불러와 확인하세요.');message('메모를 저장했습니다.');});});cancel.addEventListener('click',()=>action(cancel,async()=>{await api('/rest/v1/registrations?id=eq.'+reg.id,'DELETE');await load();message('신청을 취소했습니다. 자리가 다시 열렸습니다.');}));item.append(form);$('registrations').append(item);}
}
$('login').addEventListener('submit',e=>{e.preventDefault();action(e.submitter,async()=>{session=await api('/auth/v1/token?grant_type=password','POST',{email:$('email').value,password:$('password').value});$('password').value='';authView();await load();message('내 계정의 신청 내역을 불러왔습니다.');});});
$('logout').addEventListener('click',()=>action($('logout'),async()=>{try{await api('/auth/v1/logout','POST');}finally{session=null;authView();$('events').replaceChildren(node('p','로그인 후 모임을 확인할 수 있습니다.','empty'));$('registrations').replaceChildren(node('p','로그인 후 내 신청 내역을 확인할 수 있습니다.','empty'));message('로그아웃했습니다. 다른 계정으로 비교해 보세요.');}}));
$('refresh').addEventListener('click',()=>action($('refresh'),async()=>{await load();message('최신 신청 내역을 불러왔습니다.');}));
try{const response=await fetch('/config.json');if(!response.ok)throw new Error('앱 폴더에서 npm run setup을 먼저 실행하세요.');config=await response.json();message('연습 계정으로 로그인해 주세요.');}catch(e){message(e.message,true);}
