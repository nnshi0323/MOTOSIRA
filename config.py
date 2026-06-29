import os

# ── Paths ──────────────────────────────────────────────
BASE_DIR        = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH      = os.path.join(BASE_DIR, "model", "trained", "motosira_rf.pkl")
SCALER_PATH     = os.path.join(BASE_DIR, "model", "trained", "scaler.pkl")
TRAINING_DIR    = os.path.join(BASE_DIR, "model", "training_data")
LOG_DIR         = os.path.join(BASE_DIR, "logs")
DB_PATH         = os.path.join(BASE_DIR, "dashboard", "motosira.db")

# ── Audio ───────────────────────────────────────────────
SAMPLE_RATE     = 22050
DURATION        = 3
N_MFCC          = 40

# ── MQTT ────────────────────────────────────────────────
MQTT_BROKER     = "localhost"
MQTT_PORT       = 1883
MQTT_TOPIC_AUDIO   = "motosira/audio"
MQTT_TOPIC_RESULT  = "motosira/result"

# ── Classes ─────────────────────────────────────────────
CLASSES = ["normal", "knocking", "misfire", "valve_ticking"]

SEVERITY = {
    "normal":        {"level": 0, "color": "green",  "action": "Engine OK"},
    "knocking":      {"level": 3, "color": "red",    "action": "Check fuel grade and ignition timing"},
    "misfire":       {"level": 2, "color": "orange", "action": "Check spark plug and carburetor"},
    "valve_ticking": {"level": 1, "color": "yellow", "action": "Check valve clearance"},
}