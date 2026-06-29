import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
import wave
import struct
import random
import json
import paho.mqtt.client as mqtt  # type: ignore
import config

print("=== MOTOSIRA Mock Pi Simulator ===")
print(f"Connecting to MQTT broker at {config.MQTT_BROKER}:{config.MQTT_PORT}...")

client = mqtt.Client()
client.connect(config.MQTT_BROKER, config.MQTT_PORT, 60)
client.loop_start()
print("Connected!\n")

def generate_fake_audio():
    samples = []
    freq = random.choice([100, 200, 440, 880])
    for i in range(config.SAMPLE_RATE * config.DURATION):
        val = int(32767 * 0.3 * __import__('math').sin(
            2 * __import__('math').pi * freq * i / config.SAMPLE_RATE
        ))
        samples.append(val)
    return samples

try:
    recording_num = 1
    while True:
        print(f"[Recording {recording_num}] Capturing {config.DURATION}s of audio...")
        samples = generate_fake_audio()
        
        payload = json.dumps({
            "recording_id": recording_num,
            "sample_rate": config.SAMPLE_RATE,
            "duration": config.DURATION,
            "samples_count": len(samples),
            "timestamp": time.time()
        })
        
        client.publish(config.MQTT_TOPIC_AUDIO, payload)
        print(f"[Recording {recording_num}] Sent to dashboard via MQTT")
        print(f"  Topic: {config.MQTT_TOPIC_AUDIO}")
        print(f"  Samples: {len(samples)}")
        print()
        
        recording_num += 1
        time.sleep(5)

except KeyboardInterrupt:
    print("\nSimulator stopped.")
    client.loop_stop()
    client.disconnect()