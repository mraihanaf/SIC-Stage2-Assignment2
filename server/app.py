from flask import Flask, request, jsonify
from dotenv import load_dotenv
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import os
load_dotenv()
app =  Flask(__name__)

MONGO_URI = os.getenv("MONGODB_URI")
client = MongoClient(MONGO_URI, server_api=ServerApi('1'))
db = client["unovastra"]
collection = db["sensor_data"]

@app.route("/")
def index():
    return "Unovastra API"

@app.route("/api/v1/sensor-data", methods=["POST"])
def postSensorData():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400
    result = collection.insert_one(data)
    return jsonify({"message": "Data stored successfully", "id": str(result.inserted_id)}), 201
