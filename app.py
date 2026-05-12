from flask import Flask, request, Response, render_template_string
import requests
import json
import os
import re

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VIDEO_PATH = os.path.join(BASE_DIR, "1.mp4")

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen2.5:1.5b"


@app.route("/")
def index():
    return render_template_string("""










<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>长安互动系统</title>

<style>

body{
margin:0;
overflow:hidden;
font-family:KaiTi;
}

/* 视频容器 防止白边 */
#videoBox{
position:fixed;
width:100%;
height:100%;
overflow:hidden;
z-index:-1;
}

#bgvideo{
width:100%;
height:100%;
object-fit:cover;
position:absolute;
left:0;
top:0;
transition:transform 0.8s ease;
}

/* 点击区域 */

.role{
position:absolute;
cursor:pointer;
border-radius:20px;
transition:all 0.3s ease;
display:flex;
align-items:center;
justify-content:center;
color:white;
font-weight:bold;
text-shadow:2px 2px 4px rgba(0,0,0,0.8);
overflow:hidden;
background:transparent;
backdrop-filter:none;
}

.role:hover{
background:rgba(255,215,0,0.2);
box-shadow:0 0 15px rgba(255,215,0,0.6);
transform:scale(1.08);
z-index:10;
}

.role::before{
content:attr(data-role);
display:none;
font-size:18px;
background:rgba(0,0,0,0.8);
padding:8px 12px;
border-radius:10px;
border:1px solid rgba(255,215,0,0.5);
}

.role:hover::before{
display:block;
animation:fadeIn 0.3s ease;
}

@keyframes fadeIn{
from {opacity:0; transform:translateY(10px);}
to {opacity:1; transform:translateY(0);}
}

#merchant{ left:5%; top:58%; width:16%; height:32%; }
#envoy{ left:21%; top:46%; width:16%; height:38%; }
#artist{ left:40%; top:40%; width:18%; height:48%; }
#minority{ left:57%; top:46%; width:16%; height:38%; }  
#official{ left:76%; top:43%; width:13%; height:50%; }

/* 对话框 */

#chat{
position:absolute;
bottom:30px;
left:50%;
transform:translateX(-50%);
width:90%;
max-width:800px;
background:rgba(255,255,255,0.95);
padding:20px;
border-radius:20px;
box-shadow:0 5px 20px rgba(0,0,0,0.2);
}

#answer{
min-height:70px;
font-size:19px;
margin-bottom:15px;
line-height:1.4;
color:#333;
}

.input-container{
display:flex;   
align-items:center;
}

input{
flex:1;
padding:12px;
font-size:16px;
border:1px solid #ddd;
border-radius:10px;
outline:none;
transition:border-color 0.3s ease;
}

input:focus{
border-color:#cfa936;
box-shadow:0 0 5px rgba(207,169,54,0.3);
}

button{
padding:12px 20px;
background:#cfa936;
border:none;
color:white;
border-radius:10px;
cursor:pointer;
margin-left:10px;
transition:background 0.3s ease;
white-space:nowrap;
}

button:hover{
background:#b8942d;
}

/* 响应式设计 */
@media (max-width: 768px) {
#chat{
padding:15px;
}

button{
padding:10px 15px;
font-size:14px;
}

#answer{
font-size:17px;
}
}

</style>
</head>

<body onclick="handleBodyClick(event)">

<div id="videoBox">
<video autoplay muted loop id="bgvideo">
<source src="/video" type="video/mp4">
</video>
</div>

<div id="merchant" class="role" data-role="商人" onclick="selectRole('merchant')"></div>
<div id="envoy" class="role" data-role="外国使者" onclick="selectRole('envoy')"></div>
<div id="artist" class="role" data-role="梨园艺人" onclick="selectRole('artist')"></div>
<div id="minority" class="role" data-role="外族人" onclick="selectRole('minority')"></div>
<div id="official" class="role" data-role="官员" onclick="selectRole('official')"></div>

<div id="chat">
<div id="answer">点击人物开始互动</div>

<div class="input-container">
<input id="q" placeholder="输入问题">

<button onclick="ask()">询问</button>

<button onclick="voice()">🎤语音</button>

<button onclick="stopSpeaking()">⏹️停止</button>

<button onclick="hideAnswer()">🙈隐藏回答</button>
</div>

</div>

<script>

let role=""
let es=null

const names={
merchant:"商人",
envoy:"外国使者",
artist:"梨园艺人",
minority:"外族人",
official:"官员"
}

function selectRole(r){

role=r

/* 切换人物时关闭旧AI流 */
if(es){
es.close()
es=null
}

document.getElementById("answer").innerText="正在与 "+names[r]+" 对话"

// 不移动摄像机和碰撞箱
}

function zoomTo(r){
// 不移动摄像机和视频，保持原始状态
let video=document.getElementById("bgvideo")
video.style.transform="scale(1)"
}

function updateCollisionBoxesOnRoleChange(selectedRole){
// 不移动碰撞箱，保持位置固定
}

function ask(){

let q=document.getElementById("q").value

if(!role){
alert("请先选择人物")
return
}

if(!q){
return
}

/* 关闭旧请求 */

if(es){
es.close()
}

/* 显示思考中状态 */
document.getElementById("answer").innerText="思考中..."

/* 禁用角色切换 */
disableRoles()

/* 建立新流 */

es=new EventSource("/ask?role="+role+"&q="+encodeURIComponent(q))

let text=""

es.onmessage=function(e){

if(e.data=="[DONE]"){

speak(text)

es.close()
/* 恢复角色切换 */
enableRoles()
return

}

text+=e.data

document.getElementById("answer").innerText=text

}

}

function disableRoles(){
let roles=document.querySelectorAll('.role')
roles.forEach(function(roleEl){
    roleEl.style.pointerEvents='none'
    roleEl.style.opacity='0.5'
})
}

function enableRoles(){
let roles=document.querySelectorAll('.role')
roles.forEach(function(roleEl){
    roleEl.style.pointerEvents='auto'
    roleEl.style.opacity='1'
})
}

function voice(){

const rec=new(window.SpeechRecognition||window.webkitSpeechRecognition)()

rec.lang="zh-CN"

rec.start()

rec.onresult=function(e){

document.getElementById("q").value=e.results[0][0].transcript

}

}

function speak(text){

let u=new SpeechSynthesisUtterance(text)

u.lang="zh-CN"

// 为不同角色设置不同的音色
if(role=="merchant"){
    u.pitch=1.1; // 商人：音调稍高，显得活泼
    u.rate=1.05; // 语速稍快
} else if(role=="official"){
    u.pitch=0.9; // 官员：音调稍低，显得威严
    u.rate=0.95; // 语速稍慢
} else if(role=="envoy"){
    u.pitch=1.0; // 外国使者：音调适中
    u.rate=1.0;
} else if(role=="minority"){
    u.pitch=1.05; // 外族人：音调稍高
    u.rate=1.1;
} else if(role=="artist"){
    u.pitch=1.15; // 梨园艺人：音调较高，显得灵动
    u.rate=1.1;
}

speechSynthesis.speak(u)

}

function stopSpeaking(){
// 停止语音播报
 speechSynthesis.cancel()
// 停止AI思考（如果正在进行）
 if(es){
 es.close()
 es=null
 document.getElementById("answer").innerText="已停止思考"
 enableRoles()
 }
}

function hideAnswer(){
// 重置角色
role = "";

// 关闭旧的EventSource连接
if(es){
    es.close();
    es = null;
}

// 停止语音播报
speechSynthesis.cancel();

// 恢复对话框内容
document.getElementById("answer").innerText = "点击人物开始互动";

// 恢复所有角色碰撞箱的位置
let roles = ["merchant", "envoy", "artist", "minority", "official"];
roles.forEach(roleId => {
    let element = document.getElementById(roleId);
    if(element){
        // 恢复默认位置，与CSS中设置的一致
        if(roleId === "merchant"){
            element.style.left = "8%";
            element.style.top = "58%";
        } else if(roleId === "envoy"){
            element.style.left = "28%";
            element.style.top = "46%";
        } else if(roleId === "artist"){
            element.style.left = "48%";
            element.style.top = "40%";
        } else if(roleId === "minority"){
            element.style.left = "70%";
            element.style.top = "46%";
        } else if(roleId === "official"){
            element.style.left = "81%";
            element.style.top = "43%";
        }
        // 确保所有角色都显示
        element.style.display = "flex";
    }
});

// 恢复视频缩放
let video = document.getElementById("bgvideo");
video.style.transform = "scale(1)";

// 启用角色点击
enableRoles();
}



function updateCollisionBoxesOnRoleChange(selectedRole){
// 不移动摄像机和视频，保持碰撞箱位置固定
let basePositions = {
    merchant: { left: 8, top: 58 },
    envoy: { left: 28, top: 46 },
    artist: { left: 48, top: 40 },
    minority: { left: 70, top: 46 },
    official: { left: 86, top: 43 }
};

// 更新所有碰撞箱的位置，保持固定
Object.keys(basePositions).forEach(roleId => {
    let element = document.getElementById(roleId);
    if(element){
        let basePos = basePositions[roleId];
        // 保持碰撞箱位置固定
        element.style.left = basePos.left + '%';
        element.style.top = basePos.top + '%';
        // 确保所有碰撞箱都显示
        element.style.display = 'flex';
    }
});
}

function updateCollisionBoxesByTime(event){
// 移除随时间自动移动的功能，只在切换角色时改变位置
}

function handleBodyClick(event){
// 如果点击的不是角色碰撞箱和对话框，取消对话
if(!event.target.closest('.role') && !event.target.closest('#chat')){
    // 重置角色
    role = "";
    
    // 关闭旧的EventSource连接
    if(es){
        es.close();
        es = null;
    }
    
    // 停止语音播报
    speechSynthesis.cancel();
    
    // 恢复对话框内容
    document.getElementById("answer").innerText = "点击人物开始互动";
    
    // 恢复所有角色碰撞箱的位置
    let roles = ["merchant", "envoy", "artist", "minority", "official"];
    roles.forEach(roleId => {
        let element = document.getElementById(roleId);
        if(element){
            // 恢复默认位置，与CSS中设置的一致
            if(roleId === "merchant"){
                element.style.left = "8%";
                element.style.top = "58%";
            } else if(roleId === "envoy"){
                element.style.left = "28%";
                element.style.top = "46%";
            } else if(roleId === "artist"){
                element.style.left = "48%";
                element.style.top = "40%";
            } else if(roleId === "minority"){
                element.style.left = "70%";
                element.style.top = "46%";
            } else if(roleId === "official"){
                element.style.left = "86%";
                element.style.top = "43%";
            }
            // 确保所有角色都显示
            element.style.display = "flex";
        }
    });
    
    // 恢复视频缩放
    let video = document.getElementById("bgvideo");
    video.style.transform = "scale(1)";
}
}

</script>

</body>
</html>

""")


@app.route("/ask")
def ask():

    q = request.args.get("q","")
    role = request.args.get("role","")

    roles={
    "official":"你是生活在大唐开元盛世的官员，谈吐威严得体，熟谙当时的政治制度与社会风貌。",
    "merchant":"你是生活在大唐开元盛世的丝绸之路商人，见多识广，对当时的经济贸易了如指掌。",
    "envoy":"你是大唐开元盛世时期的外国使者，对大唐的文化繁荣与国力强盛赞叹不已。",
    "minority":"你是生活在大唐开元盛世的边疆外族人，对当时的民族融合与边疆稳定深有体会。",
    "artist":"你是生活在大唐开元盛世的梨园艺人，对当时的文化艺术发展与宫廷生活十分熟悉。"
    }

    prompt=f"{roles.get(role,'')} 请以你生活的大唐开元盛世为背景，用符合古人风韵的语言回答，语气庄重得体，100字以内，问题：{q}"

    def stream():

        r=requests.post(
        OLLAMA_URL,
        json={
        "model":MODEL_NAME,
        "prompt":prompt,
        "stream":True
        },
        stream=True)

        for line in r.iter_lines():

            if line:

                data=json.loads(line)

                if "response" in data:

                    yield f"data:{data['response']}\n\n"

                if data.get("done"):
                    break

        yield "data:[DONE]\n\n"

    return Response(stream(), mimetype="text/event-stream")


@app.route("/video")
def video():

    range_header=request.headers.get('Range',None)

    size=os.path.getsize(VIDEO_PATH)

    if not range_header:
        with open(VIDEO_PATH,'rb') as f:
            data=f.read()
        return Response(data, mimetype="video/mp4")

    byte1,byte2=0,None

    m=re.search(r'(\d+)-(\d*)',range_header)

    if m:
        byte1=int(m.group(1))
        if m.group(2):
            byte2=int(m.group(2))

    length=size-byte1

    if byte2:
        length=byte2-byte1+1

    with open(VIDEO_PATH,'rb') as f:
        f.seek(byte1)
        data=f.read(length)

    rv=Response(data,206,mimetype="video/mp4")

    rv.headers.add('Content-Range',f'bytes {byte1}-{byte1+length-1}/{size}')

    return rv


if __name__=="__main__":
    app.run(debug=True)