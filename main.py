from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import pandas as pd
import sqlite3

app = FastAPI()

def get_db():
    return sqlite3.connect("database.db")

def init_db():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users(
        username TEXT,
        password TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS devices(
        user TEXT,
        device TEXT,
        power INTEGER
    )
    """)

    conn.commit()
    conn.close()

init_db()


@app.get("/", response_class=HTMLResponse)
def home():
    return open("index.html").read()


@app.post("/login")
def login(username: str = Form(...), password: str = Form(...)):

    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT * FROM users WHERE username=? AND password=?",
                (username, password))

    data = cur.fetchone()

    if data:
        return RedirectResponse("/dashboard/"+username, status_code=303)

    return {"message":"Invalid Login"}


@app.post("/signup")
def signup(username: str = Form(...), password: str = Form(...)):

    conn = get_db()
    cur = conn.cursor()

    cur.execute("INSERT INTO users VALUES(?,?)",(username,password))
    conn.commit()

    return RedirectResponse("/",status_code=303)


@app.get("/dashboard/{user}", response_class=HTMLResponse)
def dashboard(user:str):

    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT device,power FROM devices WHERE user=?", (user,))
    devices = cur.fetchall()

    total_power = sum([d[1] for d in devices])

    tariff = 5
    cost = total_power * tariff / 1000

    html = f"""

    <h1>Smart Grid Dashboard</h1>

    <h2>Home</h2>

    Total Load: {total_power} W<br>
    Tariff: ₹{tariff}<br>
    Cost: ₹{cost}

    <h2>Devices</h2>

    <form action="/add_device" method="post">
    <input name="user" value="{user}" hidden>
    Device Name <input name="device">
    Power <input name="power">
    <button>Add</button>
    </form>

    <h3>Device List</h3>

    {devices}

    <h2>Analytics</h2>

    <a href="/export/{user}">Export Excel</a>

    """

    return HTMLResponse(html)


@app.post("/add_device")
def add_device(user:str = Form(...),
               device:str = Form(...),
               power:int = Form(...)):

    conn = get_db()
    cur = conn.cursor()

    cur.execute("INSERT INTO devices VALUES(?,?,?)",
                (user,device,power))

    conn.commit()

    return RedirectResponse("/dashboard/"+user,status_code=303)


@app.get("/export/{user}")
def export(user:str):

    conn = get_db()

    df = pd.read_sql_query(
        f"SELECT device,power FROM devices WHERE user='{user}'", conn)

    file="usage.xlsx"
    df.to_excel(file,index=False)

    return FileResponse(file,filename="usage.xlsx")
