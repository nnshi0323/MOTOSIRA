import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import time
import paho.mqtt.client as mqtt # type: ignore
import config

print("=== MOTOSIRA Dashboard Receiver ===")
print(f"Listening on topic: {config.MQTT_TOPIC_AUDIO}")
print("Waiting for data from Pi...\n")

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT broker!")
        client.subscribe(config.MQTT_TOPIC_AUDIO)
        print(f"Subscribed to {config.MQTT_TOPIC_AUDIO}\n")
    else:
        print(f"Connection failed with code {rc}")

def on_message(client, userdata, msg):
    data = json.loads(msg.payload.decode())
    print(f"Received recording #{data['recording_id']}")
    print(f"  Sample rate : {data['sample_rate']} Hz")
    print(f"  Duration    : {data['duration']}s")
    print(f"  Samples     : {data['samples_count']}")
    print(f"  Timestamp   : {time.strftime('%H:%M:%S', time.localtime(data['timestamp']))}")
    print()

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(config.MQTT_BROKER, config.MQTT_PORT, 60)
client.loop_forever()