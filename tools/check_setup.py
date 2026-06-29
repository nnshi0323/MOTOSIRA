import sys
print(f"Python: {sys.version}")

libs = [
    "pyaudio", "librosa", "soundfile", "numpy",
    "scipy", "sklearn", "joblib", "pandas",
    "matplotlib", "paho.mqtt", "flask", "flask_socketio"
]

all_good = True
for lib in libs:
    try:
        __import__(lib)
        print(f"  OK  {lib}")
    except ImportError:
        print(f"  MISSING  {lib}")
        all_good = False

if all_good:
    print("\nAll good! Ready for Phase 1.")
else:
    print("\nSome libraries missing. Run: pip install -r requirements.txt")