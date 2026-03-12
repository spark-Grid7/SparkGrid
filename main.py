from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import json, os

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# Database for Login
DB_FILE = "users.json"
if not os.path.exists(DB_FILE):
    with open(DB_FILE, "w") as f: json.dump({"admin": {"password": "spark123"}}, f)

# Device Configuration
devices = [
    {"name": "5V Pump", "pin": 26, "power": 45, "state": False, "priority": "Low"},
    {"name": "5V LED", "pin": 27, "power": 10, "state": False, "priority": "High"}
]
config = {"threshold": 100}

@app.get("/grid/live")
async def live():
    total_watts = sum(d["power"] for d in devices if d["state"])
    
    # AUTO-SHEDDING: If limit is hit, turn off 'Low' priority devices
    if total_watts > config["threshold"]:
        for d in devices:
            if d["priority"] == "Low": d["state"] = False
        total_watts = sum(d["power"] for d in devices if d["state"])

    # Prepare status for ESP32 (1=ON, 0=OFF)
    essential = 1 if next(d for d in devices if d["pin"]==26)["state"] else 0
    nonessential = 1 if next(d for d in devices if d["pin"]==23)["state"] else 0

    return {
        "watts": total_watts,
        "limit": config["threshold"],
        "essential": essential,
        "nonessential": nonessential,
        "cost": round(total_watts * 0.008, 2)
    }

@app.post("/devices/toggle")
async def toggle(data: dict):
    pin = int(data.get("pin"))
    for d in devices:
        if d["pin"] == pin: d["state"] = not d["state"]
    return {"status": "ok"}

@app.post("/grid/threshold")
async def set_limit(data: dict):
    config["threshold"] = int(data.get("limit"))
    return {"status": "ok"}

@app.get("/", response_class=HTMLResponse)
async def home():
    with open("index.html", "r", encoding="utf-8") as f: return f.read()

@app.get("/devices")
async def get_devs(): return devices
