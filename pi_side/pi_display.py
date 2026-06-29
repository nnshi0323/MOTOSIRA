import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import time
import paho.mqtt.client as mqtt  # type: ignore
import config

print("=== MOTOSIRA Pi Display Receiver ===")

def display_result(result):
    label = result.get('classification', 'unknown').replace('_', ' ').upper()
    confidence = int(result.get('confidence', 0) * 100)
    action = result.get('action', '')
    severity = result.get('severity', 0)
    timestamp = result.get('timestamp', '--:--:--')

    # Terminal display (replace with LCD library calls on real Pi)
    os.system('cls' if os.name == 'nt' else 'clear')
    print("=" * 40)
    print("       MOTOSIRA DIAGNOSIS")
    print("=" * 40)
    print(f"  Status    : {label}")
    print(f"  Confidence: {confidence}%")
    print(f"  Severity  : {severity} / 3")
    print(f"  Time      : {timestamp}")
    print("-" * 40)
    print(f"  Action: {action}")
    print("=" * 40)

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT broker!")
        client.subscribe(config.MQTT_TOPIC_RESULT)
        print(f"Listening for results on: {config.MQTT_TOPIC_RESULT}\n")

def on_message(client, userdata, msg):
    try:
        result = json.loads(msg.payload.decode())
        display_result(result)
    except Exception as e:
        print(f"Error: {e}")

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(config.MQTT_BROKER, config.MQTT_PORT, 60)
client.loop_forever()