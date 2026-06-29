import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, render_template, jsonify, request, session, redirect, url_for
from flask_socketio import SocketIO
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv
import json, time, threading
import paho.mqtt.client as mqtt  # type: ignore
import config
from database import init_db, save_recording, get_recent
from processor import extract_mfcc
from auth import login_required, check_credentials

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'motosira2024')
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per minute"],
    storage_uri="memory://"
)

latest_result = {
    "classification": "waiting",
    "confidence": 0,
    "severity": 0,
    "action": "Waiting for engine data...",
    "timestamp": None
}

def fake_classify(features):
    import random
    label = random.choice(config.CLASSES)
    confidence = round(random.uniform(0.75, 0.99), 2)
    return label, confidence

def validate_mqtt_payload(data):
    required = ['recording_id', 'sample_rate', 'duration', 'timestamp']
    for key in required:
        if key not in data:
            return False
    if not isinstance(data.get('recording_id'), int):
        return False
    if data.get('sample_rate') != config.SAMPLE_RATE:
        return False
    return True

def on_mqtt_message(client, userdata, msg):
    global latest_result
    try:
        if len(msg.payload) > 1024 * 1024:
            print("Payload too large, ignoring")
            return

        data = json.loads(msg.payload.decode())

        if not validate_mqtt_payload(data):
            print("Invalid payload, ignoring")
            return

        recording_id = data.get('recording_id', 0)
        samples = data.get('samples', [])

        if not samples:
            import math
            samples = [
                int(32767 * 0.3 * math.sin(2 * math.pi * 440 * i / config.SAMPLE_RATE))
                for i in range(config.SAMPLE_RATE * config.DURATION)
            ]

        features = extract_mfcc(samples)
        label, confidence = fake_classify(features)
        severity_info = config.SEVERITY[label]

        latest_result = {
            "classification": label,
            "confidence": confidence,
            "severity": severity_info["level"],
            "color": severity_info["color"],
            "action": severity_info["action"],
            "timestamp": time.strftime('%H:%M:%S')
        }

        save_recording(
            recording_id, time.time(),
            config.SAMPLE_RATE, config.DURATION,
            label, confidence,
            severity_info["level"],
            severity_info["action"],
            features
        )

        socketio.emit('new_result', latest_result)
        print(f"[{latest_result['timestamp']}] #{recording_id} → {label} ({confidence:.0%})")

    except json.JSONDecodeError:
        print("Invalid JSON payload, ignoring")
    except Exception as e:
        print(f"Error: {e}")

def start_mqtt():
    client = mqtt.Client()  # type: ignore
    client.on_message = on_mqtt_message
    client.connect(config.MQTT_BROKER, config.MQTT_PORT, 60)
    client.subscribe(config.MQTT_TOPIC_AUDIO)
    client.loop_forever()

# ── Auth routes ─────────────────────────────────────────
@app.route('/login', methods=['GET', 'POST'])
@limiter.limit("10 per minute")
def login():
    if session.get('logged_in'):
        return redirect(url_for('index'))
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        if check_credentials(username, password):
            session['logged_in'] = True
            session['username'] = username
            return redirect(url_for('index'))
        else:
            error = 'Invalid username or password.'
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# ── Main routes ──────────────────────────────────────────
@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/api/latest')
@login_required
@limiter.limit("60 per minute")
def api_latest():
    return jsonify(latest_result)

@app.route('/api/history')
@login_required
@limiter.limit("30 per minute")
def api_history():
    rows = get_recent(20)
    history = []
    for r in rows:
        history.append({
            "id": r[0],
            "timestamp": time.strftime('%H:%M:%S', time.localtime(r[1])),
            "classification": r[2],
            "confidence": f"{r[3]:.0%}",
            "severity": r[4],
            "action": r[5]
        })
    return jsonify(history)

@app.route('/api/export')
@login_required
def api_export():
    rows = get_recent(1000)
    lines = ['ID,Time,Classification,Confidence,Severity,Action']
    for r in rows:
        t = time.strftime('%H:%M:%S', time.localtime(r[1]))
        lines.append(f'{r[0]},{t},{r[2]},{r[3]:.0%},{r[4]},"{r[5]}"')
    csv = '\n'.join(lines)
    return app.response_class(csv, mimetype='text/csv',
        headers={'Content-Disposition': 'attachment;filename=motosira_export.csv'})

if __name__ == '__main__':
    init_db()
    mqtt_thread = threading.Thread(target=start_mqtt, daemon=True)
    mqtt_thread.start()
    print("=== MOTOSIRA Dashboard (Secured) ===")
    print("Open browser at: http://localhost:5000")
    socketio.run(app, host='0.0.0.0', port=5000, debug=False,
                 use_reloader=False, allow_unsafe_werkzeug=True)