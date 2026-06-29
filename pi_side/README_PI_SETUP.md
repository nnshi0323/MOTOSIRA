# MOTOSIRA — Raspberry Pi Setup Guide

## Hardware Required
- Raspberry Pi 4 (2GB+ RAM)
- USB Microphone or I2S MEMS Mic
- 3.5" TFT LCD Display (480x320, SPI)
- MicroSD Card (16GB+)

## Step 1 — Flash Raspberry Pi OS
Download Raspberry Pi OS (64-bit) and flash to SD card using Raspberry Pi Imager.
Enable SSH during setup for remote access.

## Step 2 — Install dependencies on Pi
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3-pip mosquitto mosquitto-clients portaudio19-dev
pip3 install pyaudio paho-mqtt numpy
```

## Step 3 — Copy Pi files
Copy these files to the Pi:
- pi_side/pi_capture.py
- pi_side/pi_display.py
- config.py

## Step 4 — Update config.py on Pi
Change MQTT_BROKER to your PC's IP address:
```python
MQTT_BROKER = "192.168.100.8"  # Your PC's IP
```

## Step 5 — Run on Pi
Terminal 1 — start audio capture:
```bash
python3 pi_capture.py
```

Terminal 2 — start display:
```bash
python3 pi_display.py
```

## Step 6 — Kiosk mode (auto-start on boot)
Add to /etc/rc.local before exit 0:
```bash
python3 /home/pi/MOTOSIRA/pi_side/pi_capture.py &
python3 /home/pi/MOTOSIRA/pi_side/pi_display.py &
```

## Step 7 — Dashboard kiosk on touchscreen
Install Chromium and add to autostart:
```bash
chromium-browser --kiosk --noerrdialogs http://192.168.100.8:5000
```

## Notes
- PC must be running dashboard/app.py before Pi starts
- Both Pi and PC must be on same WiFi network
- MQTT broker runs on PC (already installed as service)