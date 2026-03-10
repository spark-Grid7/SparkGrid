from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import random
import pandas as pd

app = FastAPI()

# Allow browser requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------
# USERS DATABASE
# -------------------------

users = {
    "admin": {"password": "spark123", "role": "admin"},
    "user1": {"password": "grid123", "role": "user"},
}

# -------------------------
# DEVICES (Example)
# -------------------------

devices = [
    {"name": "5V Pump", "pin": 23},
    {"name": "5V LED", "pin": 2}
]

# -------------------------
# LOGIN API
# -------------------------

@app.post("/login")
async def login(data: dict):

    username = data.get("username")
    password = data.get("password")

    if username in users and users[username]["password"] == password:
        return {"status": "ok", "role": users[username]["role"]}

    return JSONResponse({"error": "invalid"}, status_code=401)


# -------------------------
# LIVE GRID METRICS
# -------------------------

@app.get("/grid/live-metrics")
async def live_metrics():

    watts = round(random.uniform(40,120),2)
    amps = round(watts/230,3)
    cost = round(watts * 0.008,2)

    return {
        "watts": watts,
        "amps": amps,
        "cost": cost
    }


# -------------------------
# ANALYTICS DATA
# -------------------------

@app.get("/analytics/usage-data")
async def usage_data():

    labels = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]

    data = [
        random.randint(10,35),
        random.randint(10,35),
        random.randint(10,35),
        random.randint(10,35),
        random.randint(10,35),
        random.randint(10,35),
        random.randint(10,35),
    ]

    return {
        "labels": labels,
        "data": data
    }


# -------------------------
# ADMIN DASHBOARD DATA
# -------------------------

@app.get("/admin/all-stats")
async def admin_stats():

    stats = {}

    for u in users:
        stats[u] = {
            "devices": devices,
            "load": random.randint(50,200),
            "role": users[u]["role"]
        }

    return stats


# -------------------------
# EXPORT EXCEL
# -------------------------

@app.get("/admin/export")
async def export_excel():

    data = {
        "Day":["Mon","Tue","Wed","Thu","Fri","Sat","Sun"],
        "Usage":[
            random.randint(10,35),
            random.randint(10,35),
            random.randint(10,35),
            random.randint(10,35),
            random.randint(10,35),
            random.randint(10,35),
            random.randint(10,35),
        ]
    }

    df = pd.DataFrame(data)

    file = "energy_report.xlsx"
    df.to_excel(file,index=False)

    return FileResponse(file,filename=file)


# -------------------------
# SERVE DASHBOARD
# -------------------------

@app.get("/", response_class=HTMLResponse)
async def home():
    with open("index.html","r",encoding="utf-8") as f:
        return f.read()
