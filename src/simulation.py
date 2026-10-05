"""
Week 4 IoT Interoperability Simulation
Scenario: Smart Home Environmental Monitoring and Automated Fan Control
Protocol: MQTT
Run: python src/simulation.py
"""

from dataclasses import dataclass
import csv
import json
import random
import statistics
from pathlib import Path

random.seed(42)

OUT = Path("results")
OUT.mkdir(exist_ok=True)

@dataclass
class Device:
    device_id: str
    device_type: str
    protocol: str
    location: str

devices = [
    Device("TEMP-01", "Temperature/Humidity Sensor", "MQTT", "Living Room"),
    Device("LIGHT-01", "Light Sensor", "MQTT", "Living Room"),
    Device("FAN-01", "Smart Fan Actuator", "MQTT", "Living Room"),
    Device("EDGE-01", "Edge Gateway", "MQTT", "Living Room"),
]

def make_payload(temp, humidity, lux):
    return {
        "device_id": "TEMP-01",
        "timestamp": "2026-10-05T12:00:00Z",
        "temperature_c": round(temp, 2),
        "humidity_pct": round(humidity, 2),
        "light_lux": round(lux, 2),
    }

def validate_payload(payload):
    required = {"device_id", "timestamp", "temperature_c", "humidity_pct", "light_lux"}
    return required.issubset(payload.keys())

def simulate(iterations=50):
    rows = []
    for i in range(iterations):
        temp = 23.0 + random.random() * 8.0
        humidity = 45.0 + random.random() * 20.0
        lux = 120.0 + random.random() * 680.0

        # Normal MQTT telemetry
        payload = make_payload(temp, humidity, lux)
        valid = validate_payload(payload)

        # Simulated end-to-end latency in milliseconds
        latency_ms = max(8.0, random.gauss(82, 14))
        packet_loss = random.random() < 0.04

        # Edge rule: turn fan ON when temperature >= 28 C
        fan_command = "ON" if temp >= 28 else "OFF"
        command_latency_ms = max(10.0, random.gauss(96, 18))

        # Interoperability fault introduced in iterations 17-20:
        # an alternate sensor sends temperature as a string.
        fault = None
        if 17 <= i <= 20:
            fault = "temperature_c sent as string"
            payload["temperature_c"] = f"{temp:.2f}"

        accepted = validate_payload(payload)
        if fault:
            # Gateway schema expects numeric temperature
            accepted = isinstance(payload["temperature_c"], (int, float))

        rows.append({
            "iteration": i + 1,
            "device": "TEMP-01",
            "temperature_c": temp,
            "humidity_pct": humidity,
            "light_lux": lux,
            "payload_valid": accepted,
            "telemetry_latency_ms": round(latency_ms, 2),
            "packet_lost": packet_loss,
            "fan_command": fan_command,
            "command_latency_ms": round(command_latency_ms, 2),
            "fault": fault or "",
        })

    with open(OUT / "test_results.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    # Summary
    valid_rows = [r for r in rows if r["payload_valid"]]
    latencies = [r["telemetry_latency_ms"] for r in rows if not r["packet_lost"]]
    cmd_latencies = [r["command_latency_ms"] for r in rows]
    packet_losses = sum(r["packet_lost"] for r in rows)

    summary = {
        "iterations": iterations,
        "valid_payloads": len(valid_rows),
        "invalid_payloads": iterations - len(valid_rows),
        "payload_success_rate_pct": round(100 * len(valid_rows) / iterations, 2),
        "packet_loss_count": packet_losses,
        "packet_loss_rate_pct": round(100 * packet_losses / iterations, 2),
        "mean_telemetry_latency_ms": round(statistics.mean(latencies), 2),
        "p95_telemetry_latency_ms": round(sorted(latencies)[int(0.95 * len(latencies)) - 1], 2),
        "mean_command_latency_ms": round(statistics.mean(cmd_latencies), 2),
        "p95_command_latency_ms": round(sorted(cmd_latencies)[int(0.95 * len(cmd_latencies)) - 1], 2),
        "fan_on_events": sum(r["fan_command"] == "ON" for r in rows),
    }

    with open(OUT / "summary.json", "w") as f:
        json.dump(summary, f, indent=2)

    print(json.dumps(summary, indent=2))
    print("Results written to results/test_results.csv and results/summary.json")

if __name__ == "__main__":
    simulate()
