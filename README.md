# Week 4 IoT Device Integration and Interoperability Testing

## Scenario
Smart-home environmental monitoring with MQTT. A temperature/humidity sensor and light sensor publish telemetry to an MQTT broker. An edge gateway validates data and decides whether the smart fan should be ON or OFF.

## Files
- `src/simulation.py` - deterministic, broker-independent interoperability simulation.
- `src/mqtt_demo.py` - optional real MQTT demonstration using a local Mosquitto broker.
- `results/test_results.csv` - generated test log.
- `results/summary.json` - generated metrics.
- `requirements.txt` - Python dependency for the MQTT demo.

## Run the simulation
```bash
python src/simulation.py
```

## Run the optional MQTT demo
1. Install Mosquitto and start the broker on `localhost:1883`.
2. Install Python dependencies:
```bash
pip install -r requirements.txt
```
3. Run:
```bash
python src/mqtt_demo.py
```

## Topics
- `home/livingroom/telemetry`
- `home/livingroom/fan/cmd`

## Interoperability test
Iterations 17-20 deliberately change `temperature_c` from a number to a string. The edge gateway rejects those four messages, demonstrating a schema/data-type mismatch. The recommended production fix is a versioned JSON schema and strict validation at the gateway.
