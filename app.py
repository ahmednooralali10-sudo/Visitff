import json, asyncio, time, requests, urllib3, aiohttp, os
from Crypto.Cipher import AES
from flask import Flask, request, jsonify

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)
API_KEY = os.environ.get("API_KEY", "")
ACCS_PATH = os.environ.get("ACCS_PATH", "accs.txt")

def vr(n):
    d=[]
    while True:
        b=n&0x7F; n>>=7
        if n: b|=0x80
        d.append(b)
        if not n: break
    return bytes(d)

def pb(F):
    p=bytearray()
    for f,v in F.items():
        if isinstance(v,bool): p.extend(vr((f<<3)|0)); p.extend(vr(1 if v else 0))
        elif isinstance(v,int): p.extend(vr((f<<3)|0)); p.extend(vr(v))
        elif isinstance(v,str): d=v.encode(); p.extend(vr((f<<3)|2)); p.extend(vr(len(d))); p.extend(d)
        elif isinstance(v,(bytes,bytearray)): d=bytes(v); p.extend(vr((f<<3)|2)); p.extend(vr(len(d))); p.extend(d)
    return bytes(p)

def rv(data,pos):
    r=0;s=0
    while pos<len(data):
        b=data[pos]; pos+=1; r|=(b&0x7F)<<s
        if not(b&0x80): break
        s+=7
    return r,pos

def parse(data):
    f={}; pos=0; n=len(data)
    while pos<n:
        try: k,pos=rv(data,pos)
        except: break
        fn=k>>3; wt=k&7
        try:
            if wt==0: v,pos=rv(data,pos)
            elif wt==2: ln,pos=rv(data,pos); v=data[pos:pos+ln]; pos+=ln
            elif wt==5: v=data[pos:pos+4]; pos+=4
            elif wt==1: v=data[pos:pos+8]; pos+=8
            else: break
        except: break
        f.setdefault(fn,[]).append(v)
    return f

def enc(k,i,p):
    pl=16-(len(p)%16)
    return AES.new(k,AES.MODE_CBC,i).encrypt(p+bytes([pl]*pl))

def strip_prefix(b):
    if len(b)<=64: return b
    try:
        if 8 in parse(b): return b
    except: pass
    try:
        if 8 in parse(b[64:]): return b[64:]
    except: pass
    return b[64:]

def oauth(uid,pwd):
    H={"User-Agent":"GarenaMSDK/4.0.19P4(G011A ;Android 9;en;US;)","Content-Type":"application/json; charset=utf-8"}
    try:
        R=requests.post("https://100067.connect.garena.com/api/v2/oauth/guest/token:grant",headers=H,
            json={"client_id":100067,"client_secret":"2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3",
            "client_type":2,"device_id":"","password":pwd,"response_type":"token","uid":int(uid)},
            verify=False,timeout=20)
    except: return None
    if R.status_code not in(200,201): return None
    try: J=R.json()
    except: return None
    if J.get("code")!=0: return None
    d=J.get("data",{})
    if not d.get("access_token") or not d.get("open_id"): return None
    return d

def get_jwt(uid,pwd):
    acc=oauth(uid,pwd)
    if not acc: return None
    P={}
    P[3]=time.strftime("%Y-%m-%d %H:%M:%S");P[4]="free fire";P[5]=1;P[7]="1.132.9"
    P[8]="Android OS 14 / API-34 (UP1A.231005.007/V816.0.15.0.UNQMIXM)"
    P[9]="Handheld";P[10]="Grameenphone";P[11]="CarrierDataNetwork"
    P[12]=1666;P[13]=750;P[14]="352";P[15]="ARM64 FP ASIMD AES | 2400 | 8"
    P[16]=5563;P[17]="Mali-G57 MC2"
    P[18]="OpenGL ES 3.2 v1.r32p1-01eac0.0a0b917d9265b4c01be9925306306139"
    P[19]="Google|9cc73f7a-91f6-40f6-87ec-5b67e597eb8c";P[20]="59.152.5.188"
    P[21]="en";P[22]=acc["open_id"];P[23]="8";P[24]="Handheld"
    P[25]="Xiaomi 2312DRAABI";P[26]="BD";P[29]=acc["access_token"];P[30]=1
    P[41]="Grameenphone";P[42]="Cellular"
    P[57]="7428b253defc164018c604a1ebbfebdf"
    P[60]=109685;P[61]=58294;P[62]=797;P[63]=18000;P[64]=58818;P[65]=109685
    P[66]=58818;P[67]=109685;P[73]=2
    P[74]="/data/app/~~cqQgpdMykLQEM3odipXatw==/com.dts.freefireth-G6e5yOt1dtuXG5Ambhj18g==/lib/arm64"
    P[76]=1
    P[77]="b8e0cd5e295eee42f5860d3c86e483dd|/data/app/~~cqQgpdMykLQEM3odipXatw==/com.dts.freefireth-G6e5yOt1dtuXG5Ambhj18g==/base.apk"
    P[78]=3;P[79]=2;P[81]="64";P[83]="2019121229";P[85]=3;P[86]="OpenGLES2"
    P[87]=4095;P[88]=8
    P[89]=b"FwQVTgUPX1UaUllDDwcWCRBpWAUOUgsvA1snWlBaO1kFYg=="
    P[90]="Dhaka";P[91]="C";P[92]=8043;P[93]="android"
    P[94]="KqsHT4XbSZhqerDNUhjbS3DxG/4+I62zQU2tZFJN91kBUICAlZ5yujshLKvjlk/KiShfKfis8EeB1PMhFHIodWPncZC4fCHYF3TcTwNj95aWY/S3"
    P[95]=111207;P[96]='{"cur_rate":[60,90,120],"support_etc2":false}'
    P[97]=1;P[98]=1;P[99]="4";P[100]="4";P[102]="GQ]        e";P[103]=1
    P[104]=45174;P[105]=1
    P[106]="https://dl-bs.ggpolarbear.com/live/ABHotUpdates/|https://core-bs.ggpolarbear.com/live/ABHotUpdates/|a4332cb1c1a84e51dd77441e4856ed5a"
    P[107]="1.9393e7b8e53e8aeb"
    try:
        R=requests.post("https://loginbp.ppmainecoonghj.com/MajorLogin",
            headers={"User-Agent":"UnityPlayer/201=False8.4.12f1 (,UnityWebRequest/1.0, libtimecurl/8.5.0-DEV)",
out            "Accept":"*/*","Accept-Encoding":"deflate, gzip","X-GA-SV":str(int(time.time())),
            "Authorization":"Bearer ","X-GA":"v1 1","ReleaseVersion":"OB55",
            "Content-Type":"application/x-www-form-urlencoded","X-Unity-Version":"2018.4.12f1"},
            data=enc(b'Yg&tc%DEuh6%Zc^8',b'6oyZDr22E3ychjM%',pb(P)),verify=False,timeout=20)
    except: return None
    if R.status_code not in(200,201) or not R.content: return None
    f=parse(strip_prefix(R.content))
    j=f.get(8,[None])[0]
    s=f.get(10,[None])[0]
    if not isinstance(j,bytes): return None
    server=s.decode() if isinstance(s,bytes) else "https://clientbp.ppmainecoonghj.com"
    if not server.startswith("http"): server="https://"+server
    return j.decode(),server

def load_tokens():
    to=ks=[]
    if not os.path.exists(ACCS_PATH): return to10ks
    for ln in open(ACCS_PATH,"r",encoding="utf-8"):
        ln=ln.strip()
        if not ln or ln.startswith("#") or ":" not in ln: continue
        uid,pwd=ln.split(":",1)
        uid=uid.strip(); pwd=pwd.strip()
        if not uid or not pwd: continue
        res=get_jwt(uid,pwd)
        if res: toks.append((uid,res[0],res[1]))
        else: print(f"[fail] {uid}", flush=True)
    return toks

async def visit(session,token,server,uid):
    H={"Expect":"100-continue","Authorization":f"Bearer {token}","X-Unity-Version":"2018.4.11f1",
        "X-GA":"v1 1","ReleaseVersion":"OB55","Content-Type":"application/x-www-form-urlencoded",
        "User-Agent":"Dalvik/2.1.0 (Linux; U; Android 11; SM-A305F Build/RP1A.200720.012)",
        "Host":server.replace("https://","").replace("http://","").split("/")[0],
        "Connection":"Keep-Alive","Accept-Encoding":"gzip"}
    p=enc(b'Yg&tc%DEuh6%Zc^8',b'6oyZDr22E3ychjM%',pb({1:int(uid),2:7}))
    try:
        async with session.post(server+"/GetPlayerPersonalShow",headers=H,data=p,ssl) as r:
            return r.status
    except:
        return 0

async def send(tokens,target):
    if not tokens:
        return {"ok":0,"total":0}
    connector=aiohttp.TCPConnector(limit=100)
    timeout=aiohttp.ClientTimeout(total=30)
    async with aiohttp.ClientSession(connector=connector,timeout=timeout) as session:
        tasks=[asyncio.create_task(visit(session,tok,srv,target)) for _,tok,srv in tokens]
        results=await asyncio.gather(*tasks)
        ok=sum(1 for r in results if r==200)
        return {"ok":ok,"total":len(tokens)}

# ---------- cache ----------
_CACHE={"tokens":[],"loaded_at":0.0}
def get_tokens_cached(force=False):
    now=time.time()
    if not force and _CACHE["tokens"] and now-_CACHE["loaded_at"]<300:
        return _CACHE["tokens"]
    toks=load_tokens()
    _CACHE["tokens"]=toks
    _CACHE["loaded_at"]=now
    return toks

def run_attack_sync(target):
    toks=get_tokens_cached()
    if not toks:
        return {"ok":False,"error":"no valid tokens loaded from accs.txt","success":0,"total":0}
    try:
        res=asyncio.run(send(toks,target))
        return {"ok":True,"success":res["ok"],"total":res["total"]}
    except Exception as e:
        return {"ok":False,"error":str(e),"success":0,"total":len(toks)}

# ---------- HTTP ----------
HTML = """<!DOCTYPE html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>FF Visit Tool</title>
<style>
body{background:#06070e;color:#eef0fc;font-family:system-ui;padding:20px;max-width:560px;margin:0 auto}
h1{background:linear-gradient(135deg,#8b5cf6,#3b82f6);-webkit-background-clip:text;-webkit-text-fill-color:transparent;font-weight:900}
input,button{width:100%;padding:14px;margin:8px 0;border-radius:10px;border:1px solid #1f2440;background:#0d0f1b;color:#fff;font-size:16px;box-sizing:border-box}
button{background:linear-gradient(135deg,#8b5cf6,#3b82f6);border:none;font-weight:800;cursor:pointer}
#result{margin-top:16px;padding:14px;border-radius:10px;background:#0d0f1b;border:1px solid #1f2440;font-family:monospace;font-size:12px;white-space:pre-wrap;min-height:40px;word-break:break-all}
.small{color:#8a90b0;font-size:12px}
</style></head><body>
<h1>Free Fire Visit Tool</h1>
<p class="small">POST /api/visit { target: "UID" }</p>
<input id="target" placeholder="Target UID" inputmode="numeric">
<button onclick="go()">Send Visit</button>
<div id="result">Ready.</div>
<script>
async function go(){
  const t=document.getElementById('target').value.trim();
  const r=document.getElementById('result');
  if(!t||!/^\\d+$/.test(t)){r.textContent='Target UID must be digits only.';return;}
  r.textContent='Sending...';
  try{
    const res=await fetch('/api/visit',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({target:t})});
    const j=await res.json();
    r.textContent=JSON.stringify(j,null,2);
  }catch(e){r.textContent='error: '+e.message;}
}
</script></body></html>"""

@app.route("/")
def index():
    return HTML

@app.route("/health")
def health():
    return {"status":"ok"}

@app.route("/api/visit", methods=["POST"])
def api_visit():
    if API_KEY:
        if request.headers.get("X-API-Key","") != API_KEY:
            return jsonify({"ok":False,"error":"unauthorized"}), 401
    data=request.get_json(silent=True) or {}
    target=str(data.get("target","")).strip()
    if not target or not target.isdigit():
        return jsonify({"ok":False,"error":"target UID required (digits only)"}), 400
    return jsonify(run_attack_sync(target))

@app.route("/api/reload", methods=["POST"])
def api_reload():
    if API_KEY:
        if request.headers.get("X-API-Key","") != API_KEY:
            return jsonify({"ok":False,"error":"unauthorized"}), 401
    toks=get_tokens_cached(force=True)
    return jsonify({"ok":True,"tokens":len(toks)})

if __name__=="__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT",5000)))
