import os
from pathlib import Path
from datetime import datetime

import requests
import feedparser
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

BASE_DIR = Path(__file__).resolve().parent
root_path = os.getenv("ROOT_PATH", "")

app = FastAPI(root_path=root_path)

# Mount static and template dirs
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# Configuration
OWM_KEY = os.getenv("OWM_KEY")
OWM_CITY = os.getenv("OWM_CITY", "Berlin,de")
NEWS_FEED = os.getenv("NEWS_FEED", "https://www.tagesschau.de/xml/rss2")
QUOTE_API = os.getenv("QUOTE_API", "https://quotes.rest/qod?language=de")

def get_weather():
    url = f"https://api.openweathermap.org/data/2.5/forecast?appid={OWM_KEY}&units=metric&q={OWM_CITY}"
    data = requests.get(url).json()
    now = data.get("list", [])[0]
    current = {
        "temp": round(now["main"]["temp"]),
        "icon": now["weather"][0]["icon"],
        "desc": now["weather"][0]["description"].title(),
        "humidity": now["main"]["humidity"],
        "wind": round(now["wind"]["speed"] * 3.6),
    }
    hours = []
    for entry in data["list"][1:5]:
        dt = datetime.fromtimestamp(entry["dt"])
        hours.append({
            "time": dt.strftime("%H:%M"),
            "temp": round(entry["main"]["temp"]),
            "icon": entry["weather"][0]["icon"],
        })
    return {"current": current, "hourly": hours}

def get_news():
    feed = feedparser.parse(NEWS_FEED)
    return [entry.title for entry in feed.entries[:3]]

def get_quote():
    try:
        r = requests.get(QUOTE_API).json()
        return r["contents"]["quotes"][0]["quote"]
    except:
        return "Heute ist ein guter Tag, etwas Neues zu lernen."

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/data")
async def api_data():
    now = datetime.now()
    return JSONResponse({
        "time": now.strftime("%H:%M"),
        "date": now.strftime("%A, %d. %B"),
        "weather": get_weather(),
        "news": get_news(),
        "quote": get_quote(),
    })
