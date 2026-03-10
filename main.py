from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import json, os

app = FastAPI()
DB = "users.json"

if not os.path.exists(DB):
    with open(DB, "w") as f: json.dump({"admin": "spark123"}, f)

@app.get("/")
async def home():
    with open("index.html", "r") as f: return HTMLResponse(f.read())

@app.post("/register")
async def register(req: Request):
    data = await req.json()
    with open(DB, "r") as f: users = json.load(f)
    users[data['u']] = data['p']
    with open(DB, "w") as f: json.dump(users, f)
    return {"ok": True}

@app.post("/login")
async def login(req: Request):
    data = await req.json()
    with open(DB, "r") as f: users = json.load(f)
    if users.get(data['u']) == data['p']:
        return {"ok": True, "user": data['u']}
    return {"ok": False}
