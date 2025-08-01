import random
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
import sqlite3
import os
import requests
import time

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
    vin: int
    gps: tuple
    speed: int
    engine: str
    fuel: int
    odometer: int
    diagonstic_codes: int

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



def update_data():

    pass
'''
while True:
    time.sleep(30)
    update_data()
'''

