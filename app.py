from flask import Flask, request, Response, render_template_string
import requests
from requests.auth import HTTPBasicAuth

app = Flask(__name__)

AUTH_ID    = "MAZWM1MMZIZDVKY2Y2OG"
AUTH_TOKEN = "YmVmMzc5MTAyZTM1MDBlZTQ1ZmEyMDAwYWFiOWRj"
PLIVO_NUMBER = "+912264232030"
ASSOCIATE_NUMBER = "02264236412"
OTP = "2202"
AUDIO_URL = "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3"
BASE_URL = "https://some-recommend-valley-berlin.trycloudflare.com"

@app.before_request
def allow_all_hosts():
    pass

def xml_response(content):
    xml = f'<?xml version="1.0" encoding="utf-8" ?><Response>{content}</Response>'
    return Response(xml, mimetype="text/xml")

HOME_HTML = """<!DOCTYPE html><html><head><title>InspireWorks IVR</title>
<style>body{font-family:sans-serif;max-width:500px;margin:80px auto;padding:0 20px}
input{width:100%;padding:10px;font-size:16px;margin:10px 0;box-sizing:border-box;border:1px solid #ccc;border-radius:6px}
button{background:#e8474c;color:white;border:none;padding:12px 24px;font-size:16px;border-radius:6px;cursor:pointer;width:100%}
.ok{background:#d4edda;color:#155724;padding:10px;margin-top:10px;border-radius:6px}
.err{background:#f8d7da;color:#721c24;padding:10px;margin-top:10px;border-radius:6px}</style></head>
<body><h1>InspireWorks IVR Demo</h1>
<input id="num" type="text" value="+91" placeholder="+91XXXXXXXXXX"/>
<button onclick="makeCall()">Make Call</button>
<div id="msg"></div>
<script>async function makeCall(){
const num=document.getElementById('num').value.trim();
const res=await fetch('/make_call',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({to:num})});
const data=await res.json();const el=document.getElementById('msg');
if(data.success){el.className='ok';el.innerText='Call initiated! UUID: '+data.call_uuid;}
else{el.className='err';el.innerText='Error: '+data.error;}}</script></body></html>"""

@app.route("/")
def home():
    return render_template_string(HOME_HTML)

@app.route("/make_call", methods=["POST"])
def make_call():
    data = request.get_json()
    to_number = data.get("to", "").strip()
    payload = {"from": PLIVO_NUMBER, "to": to_number,
                "answer_url": f"{BASE_URL}/ivr/otp", "answer_method": "GET"}
    resp = requests.post(f"https://api.plivo.com/v1/Account/{AUTH_ID}/Call/",
                         json=payload, auth=HTTPBasicAuth(AUTH_ID, AUTH_TOKEN))
    if resp.status_code in (200, 201, 202):
        return {"success": True, "call_uuid": resp.json().get("request_uuid", "")}
    return {"success": False, "error": resp.text}, 400

@app.route("/ivr/otp", methods=["GET", "POST"])
def ivr_otp():
    xml = f'<GetDigits action="{BASE_URL}/ivr/verify_otp" method="GET" numDigits="4" retries="5" timeout="10" invalidDigitsAction="repeat"><Speak>Welcome to InspireWorks. Please enter your 4 digit O T P followed by the hash key.</Speak></GetDigits><Speak>No input received. Goodbye.</Speak><Hangup/>'
    return xml_response(xml)

@app.route("/ivr/verify_otp", methods=["GET", "POST"])
def verify_otp():
    digits = request.args.get("Digits", "")
    if digits == OTP:
        xml = f'<Speak>O T P verified. Welcome!</Speak><Redirect method="GET">{BASE_URL}/ivr/level1</Redirect>'
    else:
        xml = f'<GetDigits action="{BASE_URL}/ivr/verify_otp" method="GET" numDigits="4" retries="5" timeout="10" invalidDigitsAction="repeat"><Speak>Incorrect O T P. Please try again.</Speak></GetDigits><Speak>No input. Goodbye.</Speak><Hangup/>'
    return xml_response(xml)

@app.route("/ivr/level1", methods=["GET", "POST"])
def ivr_level1():
    xml = f'<GetDigits action="{BASE_URL}/ivr/level2" method="GET" numDigits="1" retries="3" timeout="10" invalidDigitsAction="repeat"><Speak>Press 1 for English. Press 2 for Spanish.</Speak></GetDigits><Speak>No input. Goodbye.</Speak><Hangup/>'
    return xml_response(xml)

@app.route("/ivr/level2", methods=["GET", "POST"])
def ivr_level2():
    lang = request.args.get("Digits", "1")
    lang_name = "English" if lang == "1" else "Spanish" if lang == "2" else None
    if not lang_name:
        xml = f'<Speak>Invalid.</Speak><Redirect method="GET">{BASE_URL}/ivr/level1</Redirect>'
        return xml_response(xml)
    xml = f'<GetDigits action="{BASE_URL}/ivr/action?lang={lang}" method="GET" numDigits="1" retries="3" timeout="10" invalidDigitsAction="repeat"><Speak>You selected {lang_name}. Press 1 for audio message. Press 2 for live associate.</Speak></GetDigits><Speak>No input. Goodbye.</Speak><Hangup/>'
    return xml_response(xml)

@app.route("/ivr/action", methods=["GET", "POST"])
def ivr_action():
    digits = request.args.get("Digits", "")
    lang = request.args.get("lang", "1")
    if digits == "1":
        xml = f'<Speak>Please listen.</Speak><Play>{AUDIO_URL}</Play><Speak>Thank you. Goodbye.</Speak><Hangup/>'
    elif digits == "2":
        xml = f'<Speak>Connecting to a live associate.</Speak><Dial callerId="{PLIVO_NUMBER}"><Number>{ASSOCIATE_NUMBER}</Number></Dial>'
    else:
        xml = f'<Speak>Invalid.</Speak><Redirect method="GET">{BASE_URL}/ivr/level2?Digits={lang}</Redirect>'
    return xml_response(xml)

if __name__ == "__main__":
    print("=" * 50)
    print("✅ IVR running! Open http://localhost:5000")
    print(f"   Tunnel: {BASE_URL}")
    print("=" * 50)
    app.run(debug=False, port=5000, host="0.0.0.0",
            extra_files=[], use_reloader=False,
            threaded=True)
