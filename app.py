import json, asyncio, time, requests, urllib3, aiohttp
from Crypto.Cipher import AES
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def vr(n):
 d=[]
 while True:
  b=n&0x7F;n>>=7
  if n:b|=0x80
  d.append(b)
  if not n:break
 return bytes(d)

def pb(F):
 p=bytearray()
 for f,v in F.items():
  if isinstance(v,bool):p.extend(vr((f<<3)|0));p.extend(vr(1 if v else 0))
  elif isinstance(v,int):p.extend(vr((f<<3)|0));p.extend(vr(v))
  elif isinstance(v,str):d=v.encode();p.extend(vr((f<<3)|2));p.extend(vr(len(d)));p.extend(d)
  elif isinstance(v,(bytes,bytearray)):d=bytes(v);p.extend(vr((f<<3)|2));p.extend(vr(len(d)));p.extend(d)
 return bytes(p)

def rv(data,pos):
 r=0;s=0
 while pos<len(data):
  b=data[pos];pos+=1;r|=(b&0x7F)<<s
  if not(b&0x80):break
  s+=7
 return r,pos

def parse(data):
 f={};pos=0;n=len(data)
 while pos<n:
  try:k,pos=rv(data,pos)
  except:break
  fn=k>>3;wt=k&7
  try:
   if wt==0:v,pos=rv(data,pos)
   elif wt==2:ln,pos=rv(data,pos);v=data[pos:pos+ln];pos+=ln
   elif wt==5:v=data[pos:pos+4];pos+=4
   elif wt==1:v=data[pos:pos+8];pos+=8
   else:break
  except:break
  f.setdefault(fn,[]).append(v)
 return f

def enc(k,i,p):
 pl=16-(len(p)%16)
 return AES.new(k,AES.MODE_CBC,i).encrypt(p+bytes([pl]*pl))

def strip_prefix(b):
 if len(b)<=64:return b
 try:
  if 8 in parse(b):return b
 except:pass
 try:
  if 8 in parse(b[64:]):return b[64:]
 except:pass
 return b[64:]

def oauth(uid,pwd):
 H={"User-Agent":"GarenaMSDK/4.0.19P4(G011A ;Android 9;en;US;)","Content-Type":"application/json; charset=utf-8"}
 try:
  R=requests.post("https://100067.connect.garena.com/api/v2/oauth/guest/token:grant",headers=H,json={"client_id":100067,"client_secret":"2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3","client_type":2,"device_id":"","password":pwd,"response_type":"token","uid":int(uid)},verify=False,timeout=20)
 except:return None
 if R.status_code not in(200,201):return None
 try:J=R.json()
 except:return None
 if J.get("code")!=0:return None
 d=J.get("data",{})
 if not d.get("access_token") or not d.get("open_id"):return None
 return d

def get_jwt(uid,pwd):
 acc=oauth(uid,pwd)
 if not acc:return None
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
  R=requests.post("https://loginbp.ppmainecoonghj.com/MajorLogin",headers={"User-Agent":"UnityPlayer/2018.4.12f1 (UnityWebRequest/1.0, libcurl/8.5.0-DEV)","Accept":"*/*","Accept-Encoding":"deflate, gzip","X-GA-SV":str(int(time.time())),"Authorization":"Bearer ","X-GA":"v1 1","ReleaseVersion":"OB55","Content-Type":"application/x-www-form-urlencoded","X-Unity-Version":"2018.4.12f1"},data=enc(b'Yg&tc%DEuh6%Zc^8',b'6oyZDr22E3ychjM%',pb(P)),verify=False,timeout=20)
 except:return None
 if R.status_code not in(200,201) or not R.content:return None
 f=parse(strip_prefix(R.content))
 j=f.get(8,[None])[0]
 s=f.get(10,[None])[0]
 if not isinstance(j,bytes):return None
 server=s.decode() if isinstance(s,bytes) else "https://clientbp.ppmainecoonghj.com"
 if not server.startswith("http"):server="https://"+server
 return j.decode(),server

def load_tokens():
 toks=[]
 if not __import__("os").path.exists("accs.txt"):return toks
 for ln in open("accs.txt","r",encoding="utf-8"):
  ln=ln.strip()
  if not ln or ln.startswith("#") or ":" not in ln:continue
  uid,pwd=ln.split(":",1)
  uid=uid.strip();pwd=pwd.strip()
  if not uid or not pwd:continue
  res=get_jwt(uid,pwd)
  if res:toks.append((uid,res[0],res[1]))
  else:print(f"[fail] {uid}")
 return toks

async def visit(session,token,server,uid):
 H={"Expect":"100-continue","Authorization":f"Bearer {token}","X-Unity-Version":"2018.4.11f1","X-GA":"v1 1","ReleaseVersion":"OB55","Content-Type":"application/x-www-form-urlencoded","User-Agent":"Dalvik/2.1.0 (Linux; U; Android 11; SM-A305F Build/RP1A.200720.012)","Host":server.replace("https://","").replace("http://","").split("/")[0],"Connection":"Keep-Alive","Accept-Encoding":"gzip"}
 p=enc(b'Yg&tc%DEuh6%Zc^8',b'6oyZDr22E3ychjM%',pb({1:int(uid),2:7}))
 try:
  async with session.post(server+"/GetPlayerPersonalShow",headers=H,data=p,ssl=False,timeout=10) as r:
   return r.status
 except:
  return 0

async def send(tokens,target):
 if not tokens:
  print("no tokens");return
 connector=aiohttp.TCPConnector(limit=100)
 timeout=aiohttp.ClientTimeout(total=30)
 async with aiohttp.ClientSession(connector=connector,timeout=timeout) as session:
  tasks=[asyncio.create_task(visit(session,tok,srv,target)) for _,tok,srv in tokens]
  results=await asyncio.gather(*tasks)
  ok=sum(1 for r in results if r==200)
  print(f"[visit] {ok}/{len(tokens)} -> {target}")

if __name__=="__main__":
 target=input("Target UID => ").strip()
 print("[jwt] loading accounts...")
 tokens=load_tokens()
 print(f"[jwt] {len(tokens)} tokens")
 asyncio.run(send(tokens,target))
