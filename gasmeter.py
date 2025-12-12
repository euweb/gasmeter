import json
import time
import logging
import logging.config
import paho.mqtt.client as mqtt
from pathlib import Path

# Try to import GPIO handler, fall back to mock if not available
try:
    from gpio_handler import GPIOHandler as GPIOInterface
    MOCK_MODE = False
except (ImportError, RuntimeError):
    from gpio_mock import GPIOMock as GPIOInterface
    MOCK_MODE = True

# ----- CONFIG -----
GPIO_PIN = 18  # Pin 18 (GPIO 24)
STATE_FILE = Path("gas_counter_test.txt")
MQTT_CONFIG_FILE = Path("mqtt_config.json")
LOGGING_CONFIG = Path("logging.conf")
BOUNCE_TIME = 2000  # 2000ms Debounce
UNIT_PER_PULSE = 0.01  # m³ per pulse
PUBLISH_INTERVAL = 60  # regular backup interval
SIMULATE_PULSE_INTERVAL = 10  # seconds between simulated pulses (mock mode only)
# -------------------

# ----- LOGGING SETUP -----
logging.config.fileConfig(LOGGING_CONFIG)
logger = logging.getLogger('gasmeter')

if MOCK_MODE:
    logger.warning("RPi.GPIO not available - Mock mode activated")

# ----- LOAD MQTT CONFIG -----
with open(MQTT_CONFIG_FILE) as f:
    mqtt_config = json.load(f)

MQTT_HOST = mqtt_config["host"]
MQTT_PORT = mqtt_config["port"]
MQTT_USERNAME = mqtt_config.get("username", "")
MQTT_PASSWORD = mqtt_config.get("password", "")
MQTT_STATE_TOPIC = mqtt_config["state_topic"]
MQTT_SET_TOPIC = mqtt_config["set_topic"]

# ---- Load state ----
if STATE_FILE.exists():
    gas_count = float(STATE_FILE.read_text())
else:
    gas_count = 0.0


# ----- MQTT HANDLERS -----
def on_connect(client, userdata, flags, rc):
    logger.info(f"MQTT connected: {rc}")
    client.subscribe(MQTT_SET_TOPIC)

def on_message(client, userdata, msg):
    global gas_count
    if msg.topic == MQTT_SET_TOPIC:
        try:
            new_val = float(msg.payload.decode())
            gas_count = new_val
            save_state()
            client.publish(MQTT_STATE_TOPIC, gas_count, retain=True)
            logger.info(f"Counter value set from HA: {gas_count}")
        except ValueError:
            logger.error("Invalid value received.")


client = mqtt.Client()
if MQTT_USERNAME:
    client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
client.on_connect = on_connect
client.on_message = on_message
client.connect(MQTT_HOST, MQTT_PORT, 60)
client.loop_start()


def save_state():
    """Saves current counter value"""
    STATE_FILE.write_text(str(gas_count))


# ----- GPIO CALLBACK -----
def on_impulse(channel=None):
    """Called on every pulse (real or simulated)"""
    global gas_count
    gas_count += UNIT_PER_PULSE
    save_state()
    client.publish(MQTT_STATE_TOPIC, gas_count, retain=True)
    prefix = "[SIMULATED] " if MOCK_MODE else ""
    logger.info(f"{prefix}Pulse detected → new reading: {gas_count:.2f} m³")


# ----- GPIO SETUP -----
logger.info(f"Current reading: {gas_count:.2f} m³")
if MOCK_MODE:
    gpio = GPIOInterface(GPIO_PIN, BOUNCE_TIME, on_impulse, pulse_interval=SIMULATE_PULSE_INTERVAL)
else:
    gpio = GPIOInterface(GPIO_PIN, BOUNCE_TIME, on_impulse)

gpio.setup()

# ----- MAIN LOOP -----
last_publish = time.time()

try:
    while True:
        now = time.time()
        
        # regular backup
        if now - last_publish > PUBLISH_INTERVAL:
            client.publish(MQTT_STATE_TOPIC, gas_count, retain=True)
            last_publish = now
            if MOCK_MODE:
                logger.debug(f"Backup publish: {gas_count:.2f} m³")
        
        time.sleep(1)
except KeyboardInterrupt:
    logger.info("Program terminated.")
    logger.info(f"Final reading: {gas_count:.2f} m³")
    gpio.cleanup()
