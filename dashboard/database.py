import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import sqlite3
import json
import time
import config

def init_db():
    os.makedirs(os.path.dirname(config.DB_PATH), exist_ok=True)
    conn = sqlite3.connect(config.DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS recordings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recording_id INTEGER,
            timestamp REAL,
            sample_rate INTEGER,
            duration INTEGER,
            classification TEXT,
            confidence REAL,
            severity INTEGER,
            action TEXT,
            features TEXT
        )
    ''')
    conn.commit()
    conn.close()
    print("Database initialized!")

def save_recording(recording_id, timestamp, sample_rate, duration,
                   classification, confidence, severity, action, features):
    conn = sqlite3.connect(config.DB_PATH)
    c = conn.cursor()
    c.execute('''
        INSERT INTO recordings
        (recording_id, timestamp, sample_rate, duration,
         classification, confidence, severity, action, features)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        recording_id, timestamp, sample_rate, duration,
        classification, confidence, severity, action,
        json.dumps(features.tolist())
    ))
    conn.commit()
    conn.close()

def get_recent(limit=20):
    conn = sqlite3.connect(config.DB_PATH)
    c = conn.cursor()
    c.execute('''
        SELECT recording_id, timestamp, classification,
               confidence, severity, action
        FROM recordings
        ORDER BY timestamp DESC LIMIT ?
    ''', (limit,))
    rows = c.fetchall()
    conn.close()
    return rows

if __name__ == "__main__":
    print("=== Database Test ===")
    init_db()
    import numpy as np
    test_features = np.zeros(40)
    save_recording(1, time.time(), 22050, 3,
                   "normal", 0.95, 0, "Engine OK", test_features)
    save_recording(2, time.time(), 22050, 3,
                   "knocking", 0.87, 3, "Check fuel grade", test_features)
    rows = get_recent()
    print(f"\nSaved {len(rows)} recordings:")
    for r in rows:
        print(f"  #{r[0]} | {r[2]} | confidence: {r[3]:.0%} | {r[5]}")
    print("\nDatabase working correctly!")