import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pyaudio
import numpy as np
import json
import time
import paho.mqtt.client as mqtt  # type: ignore
import config

print("=== MOTOSIRA Pi Audio Capture ===")
print(f"Sample rate : {config.SAMPLE_RATE} Hz")
print(f"Duration    : {config.DURATION}s per recording")
print(f"MQTT Broker : {config.MQTT_BROKER}:{config.MQTT_PORT}")
print()

# ── MQTT setup ───────────────────────────────────────────
client = mqtt.Client()
client.connect(config.MQTT_BROKER, config.MQTT_PORT, 60)
client.loop_start()
print("Connected to MQTT broker!\n")

# ── Audio setup ──────────────────────────────────────────
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1

pa = pyaudio.PyAudio()

# Find input device
input_device = None
print("Available audio devices:")
for i in range(pa.get_device_count()):
    info = pa.get_device_info_by_index(i)
    if info['maxInputChannels'] > 0:
        print(f"  [{i}] {info['name']}")
        if input_device is None:
            input_device = i

print(f"\nUsing device index: {input_device}")

stream = pa.open(
    format=FORMAT,
    channels=CHANNELS,
    rate=config.SAMPLE_RATE,
    input=True,
    input_device_index=input_device,
    frames_per_buffer=CHUNK
)

print("Microphone ready!\n")

def record_audio():
    frames = []
    total_chunks = int(config.SAMPLE_RATE / CHUNK * config.DURATION)
    for _ in range(total_chunks):
        data = stream.read(CHUNK, exception_on_overflow=False)
        frames.append(data)
    raw = b''.join(frames)
    samples = np.frombuffer(raw, dtype=np.int16).tolist()
    return samples

recording_num = 1
try:
    while True:
        print(f"[Recording {recording_num}] Capturing {config.DURATION}s...")
        samples = record_audio()

        payload = json.dumps({
            "recording_id": recording_num,
            "sample_rate": config.SAMPLE_RATE,
            "duration": config.DURATION,
            "samples_count": len(samples),
            "samples": samples,
            "timestamp": time.time()
        })

        client.publish(config.MQTT_TOPIC_AUDIO, payload)
        print(f"[Recording {recording_num}] Sent — {len(samples)} samples")
        print()

        recording_num += 1
        time.sleep(2)

except KeyboardInterrupt:
    print("\nStopping...")
    stream.stop_stream()
    stream.close()
    pa.terminate()
    client.loop_stop()
    client.disconnect()
    print("Done.")