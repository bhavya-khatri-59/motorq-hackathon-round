from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import threading
import time
import datetime
import random
from contextlib import asynccontextmanager

class Car(BaseModel):
    vin: int
    manufacturer: str
    model: str
    fleetID: str
    owner: str
    registration: str

class Data(BaseModel):
    vin: int
    gps_lat: float
    gps_lon: float
    speed: int
    engine: str
    fuel: int
    odometer: int
    diagnostic_codes: Optional[str]
    timestamp: str

carSet = []
data_log = []
alerts = []

@asynccontextmanager
async def lifespan(app: FastAPI):
    def update_data():
        while True:
            if not carSet:
                time.sleep(30)
                continue
            car = random.choice(carSet)
            mock_data = Data(
                vin=car.vin,
                gps_lat=random.uniform(-90, 90),
                gps_lon=random.uniform(-180, 180),
                speed=random.randint(0, 120),
                engine=random.choice(['On', 'Off', 'Idle']),
                fuel=random.randint(0, 100),
                odometer=random.randint(1000, 100000),
                diagnostic_codes=None,
                timestamp=datetime.datetime.now().isoformat()
            )
            if mock_data.speed >= 80:
                alerts.append((mock_data.vin, "speed", mock_data.timestamp))
            if mock_data.fuel <= 15:
                alerts.append((mock_data.vin, "low fuel", mock_data.timestamp))
            data_log.append(mock_data)
            print(f"[Telemetry] Logged for VIN: {car.vin}")
            time.sleep(30)

    thread = threading.Thread(target=update_data, daemon=True)
    thread.start()
    yield

app = FastAPI(lifespan=lifespan)

@app.post("/vehicle/create")
def create_vehicle(car: Car):
    for c in carSet:
        if c.vin == car.vin:
            raise HTTPException(status_code=400, detail="VIN already exists")
    carSet.append(car)
    return {"message": "Vehicle added", "car": car}

@app.get("/vehicle/list")
def list_vehicles():
    return carSet

@app.post("/vehicle/delete")
def delete_vehicle(vin: int):
    global carSet
    carSet = [car for car in carSet if car.vin != vin]
    return {"message": f"Deleted car with VIN {vin}"}

@app.get("/vehicle/query")
def query_vehicle(
    vin: int = -1,
    manufacturer: str = '',
    model: str = '',
    fleetID: str = '',
    owner: str = '',
    registration: str = ''
):
    results = []
    for car in carSet:
        if (
            (vin == -1 or car.vin == vin) and
            (not manufacturer or car.manufacturer == manufacturer) and
            (not model or car.model == model) and
            (not fleetID or car.fleetID == fleetID) and
            (not owner or car.owner == owner) and
            (not registration or car.registration == registration)
        ):
            results.append(car)
    return results

@app.get("/data/telematics")
def get_telematics_log():
    return data_log[-20:]

@app.get("/alert")
def get_alerts():
    return alerts