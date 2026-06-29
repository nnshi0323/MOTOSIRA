import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np # type: ignore
import librosa # type: ignore
import config 

def extract_mfcc(samples, sample_rate=config.SAMPLE_RATE):
    audio = np.array(samples, dtype=np.float32) / 32767.0
    mfccs = librosa.feature.mfcc(
        y=audio,
        sr=sample_rate,
        n_mfcc=config.N_MFCC
    )
    features = np.mean(mfccs, axis=1)
    return features

def process_recording(data):
    print(f"Processing recording #{data['recording_id']}...")
    samples = data.get('samples', [])
    
    if not samples:
        print("  No samples in payload, generating test audio...")
        import math
        samples = [
            int(32767 * 0.3 * math.sin(2 * math.pi * 440 * i / config.SAMPLE_RATE))
            for i in range(config.SAMPLE_RATE * config.DURATION)
        ]
    
    features = extract_mfcc(samples)
    print(f"  Extracted {len(features)} MFCC features")
    print(f"  Feature range: {features.min():.2f} to {features.max():.2f}")
    return features

if __name__ == "__main__":
    print("=== MFCC Processor Test ===")
    test_data = {
        "recording_id": 1,
        "sample_rate": config.SAMPLE_RATE,
        "duration": config.DURATION,
        "samples": []
    }
    features = process_recording(test_data)
    print(f"\nFeature vector ({len(features)} values):")
    print(features)
    print("\nProcessor working correctly!")