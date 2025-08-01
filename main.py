import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import sqlite3
import random
import time
import threading
import datetime as dt
from typing import Tuple, List
from contextlib import asynccontextmanager
import uvicorn

def update_data():
    while True:
        if carSet:
            vins = [car.vin for car in carSet] if carSet else [0]
            sample_data = Data(
                vin = random.choice(vins),
                gps=(random.uniform(-90, 90), random.uniform(-180, 180)),
                speed=random.randint(0, 120),
                engine=random.choice(["On", "Off", "Idle"]),
                fuel=random.randint(0, 100),
                odometer=random.randint(1000, 200000),
                diagnostic_codes=random.randint(0,10),
                timestamp=dt.datetime.now()
            )
            try:
                requests.post("http://127.0.0.1:8000/data/update", json=sample_data.model_dump())
            except Exception as e:
                print("Data update failed:", e)
        time.sleep(1)

class BackgroundTasks(threading.Thread):
    def run(self,*args,**kwargs):
        while True:
            update_data()
            time.sleep(30)


app = FastAPI()

class Car(BaseModel):
    vin: int
    manufacturer: str
    model: str
    fleetID: str
    owner: str
    registration: str

class Data(BaseModel):
    vin: int
    gps: Tuple[float, float]
    speed: int
    engine: str
    fuel: int
    odometer: int
    diagnostic_codes: str
    timestamp: dt.datetime

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
                registration TEXT NOT NULL CHECK(registration in ('Active','Maintenance','Decommissioned'))
            )
        ''')
        conn.commit()
        conn.close()

init_db()

carSet: List[Car] = []
data_log: List[Data] = []

@app.post("/vehiclemanagement/create")
def create_car(car: Car):
    carSet.append(car)
    return car

@app.get("/vehiclemanagement/list")
def list_cars():
    return list(carSet)

@app.post("/vehiclemanagement/delete")
def delete_car(vin: int):
    for car in carSet:
        if car.vin == vin:
            carSet.remove(car)
            return {"message": "Deleted car successfully"}
    return {"message": "VIN not found"}

@app.get("/vehiclemanagement/query")
def query_cars(
    vin: int = -1,
    manufacturer: str = 'None',
    model: str = 'None',
    fleetID: str = 'None',
    owner: str = "None",
    registration: str = 'None'
):
    result = []
    for car in carSet:
        if all([
            (vin == -1 or car.vin == vin),
            (manufacturer == 'None' or car.manufacturer == manufacturer),
            (model == 'None' or car.model == model),
            (fleetID == 'None' or car.fleetID == fleetID),
            (owner == "None" or car.owner == owner),
            (registration == 'None' or car.registration == registration)
        ]):
            result.append(car)
    return result

@app.post("/data/update")
def update_telematics_data(data: Data):
    data_log.append(data)
    return data

@app.get("/data/log")
def get_data_log():
    return data_log

if __name__ == '__main__':
    t = BackgroundTasks()
    t.start()
    uvicorn.run(app, host="0.0.0.0", port=8000)