import espflask
import time

espflask.create_ap("MicroHackChat")

messages = []

app=espflask.ESPFlask("MicroHackChat")

@app.route("/")
def mainpage(request: espflask.Request):
    response=espflask.Response('<meta content="width=device-width,initial-scale=1"name=viewport><meta charset=utf-8><title>micro hack.chat</title><link href=manifest.json rel=manifest><style>ol,pre,ul{display:block}.message .text,pre{word-wrap:break-word}#footer,#sidebar{position:fixed;bottom:0}code,mark{color:#000}hr,table{margin-bottom:20px}body,td,th{padding:0}body{margin:0;overflow-y:scroll}body,input,textarea{font-family:\'DejaVu Sans Mono\',monospace;font-size:12px;tab-size:4;-moz-tab-size:4;-o-tab-size:4}input[type=checkbox]{margin:0 1em 0 0}label{vertical-align:3px}input,textarea{background:0 0;border:none;outline:0;resize:none}code,pre,table>tbody>tr:nth-child(odd)>td,table>tbody>tr:nth-child(odd)>th{background-color:#4e4e4e}h4{font-size:12px;font-weight:700}pre{line-height:1.42857143;tab-size:2;white-space:pre-wrap;tab-size:4;-moz-tab-size:4;-o-tab-size:4;word-break:break-all;border:1px solid #000;border-radius:4px;color:#797979;margin:0 auto}a{color:inherit;text-decoration:none;cursor:pointer}a:hover{text-decoration:underline}#sidebar-content ul{padding-inline-start:20px}#sidebar-content ul li{list-style:disc}ol,ul{list-style-type:disc;margin-block-start:1em;margin-block-end:1em;margin-inline-start:0;margin-inline-end:0;padding-inline-start:40px;padding:0;margin:0}ul li{list-style:inside}.hidden{display:none}.expand{height:100%}.container{max-width:600px;margin:0 auto}#messages{padding-top:2em}.message,.refmessage{padding-bottom:1em}.nick{float:left;width:16em;margin-left:-17em;margin-right:1em;text-align:right;white-space:nowrap;overflow:hidden}.trip{font-size:10px}.text{margin:0 0 0 1em}.text p{margin:0}#footer{width:100%}#chatform{border-top:1px solid}#chatinput{width:100%;padding:1em;box-sizing:border-box}#sidebar{top:0;right:0;padding:1em;border-left:1px solid;overflow-y:auto}#sidebar-content{width:180px;padding-bottom:10%}h1,h2,h3,h4,h5,h6{margin:0 3px 3px}blockquote{padding:3px 10px;margin:3px;border-left:5px solid #4e4e4e}code{padding:2px 4px;font-size:90%;border-radius:4px}hr{margin-top:20px;border:0;border-top:1px solid #4e4e4e}mark{background-color:#60ac39}table{background-color:transparent;width:100%;max-width:100%;border-spacing:0;border-collapse:collapse}table>caption+thead>tr:first-child>td,table>caption+thead>tr:first-child>th,table>colgroup+thead>tr:first-child>td,table>colgroup+thead>tr:first-child>th,table>thead:first-child>tr:first-child>td,table>thead:first-child>tr:first-child>th{border-top:0}table>thead>tr>th{border-bottom:2px solid #4e4e4e}th{text-align:left}table>tbody>tr>td,table>tbody>tr>th,table>tfoot>tr>td,table>tfoot>tr>th,table>thead>tr>td,table>thead>tr>th{padding:8px;line-height:1.42857143;vertical-align:top;border-top:1px solid #4e4e4e}img{max-width:50%;max-height:800px}ol ol,ul ul{padding-left:2em}@media only screen and (max-width:600px){.nick,.text{display:inline}#messages{border:none;padding:.5em}.message{padding-bottom:.5em}.nick{margin:0;float:none;text-align:left}#sidebar{top:.5em;bottom:auto;right:.5em;border:none}}.jebbed{background:linear-gradient(to right,#66f,#09f ,#0f0,#f39,#66f);-webkit-background-clip:text;background-clip:text;color:transparent;animation:6s ease-in-out infinite rainbow_animation;background-size:400% 100%}@keyframes rainbow_animation{0%,100%{background-position:0 0}50%{background-position:100% 0}}body,input,textarea{color:#a6a28c}#footer,body{background:#20201d}.message{border-left:1px solid rgba(125,122,104,.5)!important}.refmessage{border-left:1px solid #7d7a68!important}#chatform,#sidebar{border-color:#7d7a68}.nick{color:#6684e1}.trip{color:#6e6b5e}.text a{color:#e8e4cf}.admin .nick{color:#d73737}.mod .nick{color:#1fad83}.me .nick{color:#b854d4}.info .nick,.info .text{color:#60ac39}.warn .nick,.warn .text{color:#cfb017}#sidebar{background:#292824}</style><body style=margin-bottom:54px><article class=container><div id=messages></div></article><footer id=footer><div class=container><form class=message id=chatform><textarea autocomplete=off autofocus id=chatinput style=height:38px type=text></textarea></form></div></footer><nav id=sidebar><div id=sidebar-content><h4>Micro Hack.Chat</h4><p>Hack.Chat ON ESP-32???</div></nav><script>function pushMessage(e,s){var a=document.createElement("div");a.classList.add("message");var t=document.createElement("span");t.classList.add("nick"),a.appendChild(t);var n=document.createElement("a");n.textContent=e,t.appendChild(n);var d=document.createElement("p");return d.classList.add("text"),d.innerText=s,a.appendChild(d),window.scrollTo(0,document.body.scrollHeight),document.querySelector("#messages").appendChild(a),a}pushMessage("system","Welcome to MicroHackChat, sending handshake..."),fetch("/handshake").then(e=>{pushMessage("system","Done!")});</script>')
    response.headers.update({"Content-Type":"text/html; charset=utf-8"})
    return response

@app.route("/handshake")
def handshake(request: espflask.Request):
    return "OK"

@app.route("/internal_clock")
def get_clock(request: espflask.Request):
    return str(int(time.time()))

@app.route("/post_message")
def post_message(request: espflask.Request):
    if not request.path_args.get(b"message"):
        return "ERR_NO_MSG"
    messages.append([int(time.time()), request.path_args.get(b"message").decode()])
    return "OK"

@app.route("/message_after")
def get_message(request: espflask.Request):
    if not request.path_args.get(b"time"):
        return "ERR_NO_TIME"
    get=[]
    for msg in messages:
        if msg[0] > int(request.path_args.get(b"time").decode()):
            get.append(msg[1])
    return str(get)

app.run(8082)