import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import librosa
import joblib
import json
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, confusion_matrix
import config

def extract_features(file_path):
    try:
        audio, sr = librosa.load(file_path, sr=config.SAMPLE_RATE, duration=config.DURATION)
        if len(audio) < config.SAMPLE_RATE:
            audio = np.pad(audio, (0, config.SAMPLE_RATE - len(audio)))
        mfccs = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=config.N_MFCC)
        features = np.mean(mfccs, axis=1)
        return features
    except Exception as e:
        print(f"  Error loading {file_path}: {e}")
        return None

def load_dataset():
    X, y = [], []
    print("Loading dataset...")
    for label in config.CLASSES:
        class_dir = os.path.join(config.TRAINING_DIR, label)
        if not os.path.exists(class_dir):
            print(f"  WARNING: {class_dir} not found, skipping")
            continue
        files = [f for f in os.listdir(class_dir) if f.endswith(('.wav','.mp3','.ogg'))]
        print(f"  {label}: {len(files)} files")
        for fname in files:
            fpath = os.path.join(class_dir, fname)
            features = extract_features(fpath)
            if features is not None:
                X.append(features)
                y.append(config.CLASSES.index(label))
    return np.array(X), np.array(y)

def train():
    print("=== MOTOSIRA Model Training ===\n")
    X, y = load_dataset()

    if len(X) == 0:
        print("\nNo audio files found in training_data folders.")
        print("Add .wav files to:")
        for label in config.CLASSES:
            print(f"  model/training_data/{label}/")
        print("\nRunning with SYNTHETIC data for testing...")
        X, y = generate_synthetic_data()

    print(f"\nDataset: {len(X)} samples, {len(config.CLASSES)} classes")
    print(f"Features per sample: {X.shape[1]}")

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y, test_size=0.2, random_state=42, stratify=y
    )

    print(f"\nTrain: {len(X_train)} | Test: {len(X_test)}")
    print("\nTraining Random Forest...")

    clf = RandomForestClassifier(
        n_estimators=100,
        max_depth=None,
        min_samples_split=2,
        min_samples_leaf=1,
        random_state=42,
        n_jobs=-1
    )
    clf.fit(X_train, y_train)

    cv_scores = cross_val_score(clf, X_scaled, y, cv=5)
    print(f"\nCross-validation accuracy: {cv_scores.mean():.2%} (+/- {cv_scores.std():.2%})")

    y_pred = clf.predict(X_test)
    print(f"Test accuracy: {(y_pred == y_test).mean():.2%}")

    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=config.CLASSES))

    print("Confusion Matrix:")
    print(confusion_matrix(y_test, y_pred))

    os.makedirs(os.path.join(config.BASE_DIR, "model", "trained"), exist_ok=True)
    joblib.dump(clf, config.MODEL_PATH)
    joblib.dump(scaler, config.SCALER_PATH)

    meta = {
        "classes": config.CLASSES,
        "n_features": X.shape[1],
        "n_estimators": 100,
        "training_samples": len(X),
        "cv_accuracy": float(cv_scores.mean()),
        "test_accuracy": float((y_pred == y_test).mean())
    }
    meta_path = os.path.join(config.BASE_DIR, "model", "trained", "model_meta.json")
    with open(meta_path, 'w') as f:
        json.dump(meta, f, indent=2)

    print(f"\nModel saved to: {config.MODEL_PATH}")
    print(f"Scaler saved to: {config.SCALER_PATH}")
    print(f"Metadata saved to: {meta_path}")
    print("\nTraining complete!")

def generate_synthetic_data():
    import math
    print("Generating synthetic audio features...")
    X, y = [], []
    np.random.seed(42)
    patterns = {
        0: (440,  0.1),
        1: (880,  0.4),
        2: (220,  0.3),
        3: (660,  0.2),
    }
    for label_idx, (freq, noise) in patterns.items():
        for _ in range(50):
            samples = np.array([
                int(32767 * 0.3 * math.sin(2 * math.pi * freq * i / config.SAMPLE_RATE))
                for i in range(config.SAMPLE_RATE * config.DURATION)
            ], dtype=np.float32) / 32767.0
            samples += np.random.normal(0, noise, len(samples))
            mfccs = librosa.feature.mfcc(y=samples, sr=config.SAMPLE_RATE, n_mfcc=config.N_MFCC)
            features = np.mean(mfccs, axis=1)
            X.append(features)
            y.append(label_idx)
    return np.array(X), np.array(y)

if __name__ == "__main__":
    train()