import random
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
import sqlite3
import os
import requests
import time
import datetime

app = FastAPI()

'''
VIN (Vehicle Identification Number) - unique identifier
Manufacturer and Model
Fleet ID (vehicles can belong to different fleets like "Corporate", "Rental", "Personal")
Owner/Operator information
Registration status (Active, Maintenance, Decommissioned)
'''

class Car(BaseModel):
    vin: int
    manufacturer: str
    model: str
    fleetID: str
    owner: str
    registration: str

'''
GPS coordinates (latitude, longitude)
Speed (current speed in km/h)
Engine status (On/Off/Idle)
Fuel/Battery level (percentage)
Odometer reading (total kilometers)
Diagnostic codes (if any errors)
Timestamp of the reading
'''

class Data(BaseModel):
    car: Car
    gps: tuple
    speed: int
    engine: str
    fuel: int
    odometer: int
    diagonstic_codes: int
    timestamp: datetime

def init_db():
    if not os.path.exists("cars.db"):
        conn = sqlite3.connect("cars.db")
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE Cars (
                vin INTEGER PRIMARY KEY,
                manufacturer TEXT NOT NULL,
                model TEXT NOT NULL,
                fleetID TEXT NOT NULL CHECK(fleetID in ('Corporate','Rental','Personal')),
                owner TEXT NOT NULL,
                registration TEXT NOT NULL CHECK(registration in ('Active','Maintenance','Decommissioned')
            )
        ''')
        conn.commit()
        conn.close()

init_db()

def get_db():
    conn = sqlite3.connect("cars.db", check_same_thread = False)
    try:
        yield conn
    finally:
        conn.close()

carSet = []

@app.post("/vehiclemanagement/create")
def create_user(car: Car):
    carSet.append(car)
    return car

@app.get('/vehiclemanagement/list')
def list_users():
    return list(carSet)

@app.post('/vehiclemanagement/delete')
def delete(vin: int):
    for car in carSet:
        if car.vin == vin:
            carSet.remove(car)
            return {"message": "Deleted car succesfully"}
    return {"message": "Failed"}

@app.get('/vehiclemanagement/query')
def query(vin: int = -1, manufacturer: str = 'None', model: str = 'None', fleetID: str = 'None', owner: str = "None", registration: str='None'):
    result = []
    for car in carSet:
        if all([
            (vin == -1 or car.vin == vin), (manufacturer == 'None' or manufacturer == car.manufacturer),
            (model == 'None' or car.model == model), (fleetID == 'None' or fleetID == car.fleetID),
            (owner == "None" or car.owner == owner), (registration == 'None' or registration == car.registration)
            ]): 
            result.append(car)
    return result
'''
GPS coordinates (latitude, longitude)
Speed (current speed in km/h)
Engine status (On/Off/Idle)
Fuel/Battery level (percentage)
Odometer reading (total kilometers)
Diagnostic codes (if any errors)
Timestamp of the reading
'''

def update_data():
    data = {
        "car": random.choice(carSet),
        "gps": (random.randint(1,10), random.randint(1, 10)),
        "speed": random.randint(40, 100),
        "engine": random.choice(['On', 'Off', 'Idle']),
        "fuel": random.randint(0, 100),
        "odometer": random.randint(0, 100),
        "diagnostic_codes": None,
        "timestamp": datetime.now()
        }
    url = "http://127.0.0.1:8000/data/update"
    response = requests.post(url, data)
    if response.status_code == 200:
        print("POST request successful:")
        print(response.json())
    else:
        print(f"POST request failed with status code: {response.status_code}")

data_log = []

@app.post("/data/update")
def update_telementary_data(data: Data):
    data_log.append(data)
    return data

while True:
    time.sleep(30)
    update_data()

