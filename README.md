# PlantSense Prototype
This prototype project, utilize ESP32 to sends sensor data to backend REST api and Ubidots dashboard. 

## Flow
1.  **ESP32 (MicroPython)** reads sensor data (temperature)
2. **ESP32** sent data to **Ubidots** using **MQTT**
3. **ESP32** also sends data to **Flask Server** via **REST API (POST REQUEST)**
4. **Flask Server** Processes the data and stores it in a **database**

## Instruction
**Hardware**: ESP32, LDR sensor, DHT22, Ultrasonic Sensor.
**Software**: 
- MicroPython installed on ESP32.
- Ampy for uploading MicroPython scripts.
- Flask for backend
- Ubidots account

## Install firmware to the ESP32
1. download **MicroPython Firmware**
2. Change the the required variables in `esp32-firmware/main.py`
3. Flash the `main.py` file.


## Run the REST Server
```sh
cd server
docker-compose up
```
or
```sh
pipenv install
pipenv run dev
# you can ran in prod mode too
pipenv run prod
```
