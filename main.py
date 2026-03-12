from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import random
import json
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- DATABASE SETUP ---
DB_FILE = "users.json"
if not os.path.exists(DB_FILE):
    with open(DB_FILE, "w") as f:
        json.dump({"admin": {"password": "spark123", "role": "admin"}}, f)

# Initial Device List for your 5V Motor and LED
devices = [
    {"name": "5V Pump", "pin": 23, "state": False, "power": 45, "priority": "High"},
    {"name": "5V LED", "pin": 2, "state": False, "power": 10, "priority": "Low"}
]
config = {"threshold": 100}

@app.get("/devices")
async def get_devices(): return devices

@app.post("/login")
async def login(data: dict):
    u, p = data.get("username"), data.get("password")
    with open(DB_FILE, "r") as f: users = json.load(f)
    if u in users and str(users[u]["password"]) == str(p):
        return {"status": "ok", "role": users[u]["role"]}
    return JSONResponse({"error": "Unauthorized"}, status_code=401)

@app.post("/devices/add")
async def add_device(data: dict):
    devices.append({
        "name": data.get("name"), 
        "pin": int(data.get("pin")), 
        "state": False, 
        "power": 25, 
        "priority": "Medium"
    })
    return {"status": "added"}

@app.post("/devices/remove")
async def remove_device(data: dict):
    pin = int(data.get("pin"))
    global devices
    devices = [d for d in devices if d["pin"] != pin]
    return {"status": "removed"}

# --- NEW TOGGLE ROUTE ADDED HERE ---
@app.post("/devices/toggle")
async def toggle_device(data: dict):
    pin = int(data.get("pin"))
    for d in devices:
        if d["pin"] == pin:
            d["state"] = not d["state"] 
            return {"status": "success", "new_state": d["state"]}
    return JSONResponse({"error": "Not found"}, status_code=404)

@app.post("/devices/update-priority")
async def up_prio(data: dict):
    pin, prio = int(data.get("pin")), data.get("priority")
    for d in devices:
        if d["pin"] == pin: d["priority"] = prio
    return {"status": "ok"}

@app.post("/grid/threshold")
async def set_thresh(data: dict):
    config["threshold"] = int(data.get("limit"))
    return {"status": "ok"}

@app.get("/grid/live")
async def live():
    w = sum(d["power"] for d in devices if d["state"])
    return {"watts": w, "amps": round(w/230, 3), "cost": round(w*0.008, 2), "limit": config["threshold"]}

@app.get("/admin/export")
async def export_excel():
    df = pd.DataFrame({"Day": ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"], "Load": [random.randint(40,150) for _ in range(7)]})
    df.to_excel("report.xlsx", index=False)
    return FileResponse("report.xlsx", filename="SparkGrid_Report.xlsx")

@app.get("/", response_class=HTMLResponse)
async def home():
    with open("index.html", "r", encoding="utf-8") as f: return f.read()
