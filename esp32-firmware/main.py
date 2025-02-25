from machine import Pin, ADC
import network
import ujson
import dht
import utime
import urequests
from umqtt.simple import MQTTClient

WIFI_SSID = "YOUR_WIFI_SSID"
WIFI_PASS = "YOUR_WIFI_PASS"

UBIDOTS_TOKEN = "YOUR_UBIDOTS_TOKEN"
MQTT_BROKER = "things.ubidots.com"
MQTT_PORT = 1883
DEVICE_LABEL = "esp32"
TOPIC = f"/v1.6/devices/{DEVICE_LABEL}" 

REST_API_URL = "http://YOUR_REST_API:5000/api/v1/sensor-data"  # Change this to your REST API URL

ECHO_PIN = 25
TRIG_PIN = 33
DHT11_PIN = 32
LDR_PIN = 35
SOIL_POWER_PIN = 13
SOIL_PIN = 14

dht_sensor = dht.DHT11(Pin(DHT11_PIN))
ultrasonic_trig = Pin(TRIG_PIN, Pin.OUT)
ultrasonic_echo = Pin(ECHO_PIN, Pin.IN)
ldr = ADC(Pin(LDR_PIN))
power_soil = Pin(SOIL_POWER_PIN, Pin.OUT)
soil = ADC(Pin(SOIL_PIN))

# Constants for LDR Calculation
GAMMA = 0.7
RL10 = 85  # Resistance of LDR at 10 lux

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(WIFI_SSID, WIFI_PASS)
    
    print("Connecting to Wi-Fi", end="")
    while not wlan.isconnected():
        print(".", end="")
        utime.sleep(1)
    print("\nConnected to Wi-Fi!")
    print("IP Address:", wlan.ifconfig()[0])

client = MQTTClient("esp32", MQTT_BROKER, port=MQTT_PORT, user=UBIDOTS_TOKEN, password="", ssl=False)

def connect_mqtt():
    try:
        client.connect()
        print("Connected to Ubidots MQTT Broker!")
    except Exception as e:
        print("Failed to connect to MQTT:", e)

def measureUltrasonic():
    ultrasonic_trig.value(0)
    utime.sleep_us(2)
    ultrasonic_trig.value(1)
    utime.sleep_us(5)
    ultrasonic_trig.value(0)
    
    while ultrasonic_echo.value() == 0:
        signaloff = utime.ticks_us()
    while ultrasonic_echo.value() == 1:
        signalon = utime.ticks_us()
    
    time_passed = signalon - signaloff
    distance = (time_passed * 0.0330) / 2 
    return distance

def measureLDR():
    analogValue = ldr.read()
    
    voltage = analogValue / 4095.0 * 3.3  
    if abs(3.3 - voltage) < 1e-6:
        return float('inf')

    resistance = 100000 * voltage / (3.3 - voltage)  # using 10kΩ fixed resistor

    if resistance <= 0:
        return 0  # return 0 lux instead of an error
    lux = pow(max(RL10 * 1e3 * pow(10, GAMMA) / resistance, 1e-6), (1 / GAMMA))

    return round(lux, 2)

def measureDHT():
    dht_sensor.measure()

def measureSoilMoist():
    try:
        power_soil.value(1)
        utime.sleep_ms(10)
        raw = soil.read()
        power_soil.value(0)
        voltage = (raw / 4095.0) * 3.3
        moisture = (voltage / 3.3) * 100
        return moisture
    except:
        return None

def readSensors():
    measureDHT()
    lux = measureLDR()
    distance = measureUltrasonic()
    soilMoist = measureSoilMoist()
    
    return {
        "temperature": dht_sensor.temperature(),
        "humidity": dht_sensor.humidity(),
        "lux": lux,
        "distance": distance,
        "soil_moisture": soilMoist
    }

def publish_mqtt(data):
    payload = ujson.dumps({
        "temperature": {"value": data["temperature"]},
        "humidity": {"value": data["humidity"]},
        "lux": {"value": data["lux"]},
        "distance": {"value": data["distance"]},
        "soil_moisture": {"value": data["soil_moisture"]}
    })
    
    print("Publishing to MQTT:", payload)

    try:
        client.publish(TOPIC, payload)
        print("Data sent to MQTT successfully!")
    except Exception as e:
        print("Failed to publish MQTT data:", e)

def send_http(data):
    headers = {"Content-Type": "application/json"}
    try:
        response = urequests.post(REST_API_URL, data=ujson.dumps(data), headers=headers)
        print("HTTP Response:", response.text)
        response.close()
    except Exception as e:
        print("Failed to send HTTP request:", e)

connect_wifi()
connect_mqtt()

while True:
    try:
        sensor_data = readSensors()
        publish_mqtt(sensor_data)
        send_http(sensor_data)
    except Exception as e:
        print("Error:", e)
    utime.sleep(2)

