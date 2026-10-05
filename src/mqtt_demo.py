"""
Optional MQTT integration demo.

Requirements:
    pip install paho-mqtt

Start an MQTT broker locally (for example Mosquitto), then run:
    python src/mqtt_demo.py

The script publishes sensor telemetry and subscribes to the fan command topic.
"""

import json
import time
import random
import paho.mqtt.client as mqtt

BROKER = "localhost"
PORT = 1883
TELEMETRY_TOPIC = "home/livingroom/telemetry"
COMMAND_TOPIC = "home/livingroom/fan/cmd"

def on_connect(client, userdata, flags, reason_code, properties=None):
    print("Connected to broker:", reason_code)
    client.subscribe(COMMAND_TOPIC)

def on_message(client, userdata, msg):
    print("FAN COMMAND:", msg.payload.decode())

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_connect = on_connect
client.on_message = on_message
client.connect(BROKER, PORT, 60)
client.loop_start()

try:
    for _ in range(10):
        temp = round(23 + random.random() * 8, 2)
        payload = {
            "device_id": "TEMP-01",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "temperature_c": temp,
            "humidity_pct": round(45 + random.random() * 20, 2)
        }
        client.publish(TELEMETRY_TOPIC, json.dumps(payload), qos=1)
        command = "ON" if temp >= 28 else "OFF"
        client.publish(COMMAND_TOPIC, command, qos=1)
        time.sleep(1)
finally:
    client.loop_stop()
    client.disconnect()
