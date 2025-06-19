import os
from datetime import datetime, timedelta
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import requests
import feedparser

BASE_DIR = Path(__file__).resolve().parent
root_path = os.getenv("ROOT_PATH", "")
app = FastAPI(root_path=root_path)

# Mount static + templates
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

print(f"FastAPI app created with root_path: '{app.root_path}'")

# ENV config
OWM_KEY = os.getenv("OWM_KEY")
OWM_CITY = os.getenv("OWM_CITY", "Berlin,de")
NEWS_FEED = os.getenv("NEWS_FEED", "https://www.tagesschau.de/xml/rss2")
QUOTE_API = os.getenv("QUOTE_API", "https://quotes.rest/qod?language=de")

# Caches
cache = {
    "weather": {"data": None, "expires": datetime.min},
    "news": {"data": None, "expires": datetime.min},
    "quote": {"data": None, "expires": datetime.min},
    "date": {"data": None, "expires": datetime.min},
}

def get_weather():
    if cache["weather"]["expires"] < datetime.now():
        try:
            url = f"https://api.openweathermap.org/data/2.5/forecast?appid={OWM_KEY}&units=metric&q={OWM_CITY}"
            data = requests.get(url).json()
            now = data["list"][0]
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
            cache["weather"] = {
                "data": {"current": current, "hourly": hours},
                "expires": datetime.now() + timedelta(hours=2),
            }
        except:
            pass  # On failure, keep last known data
    return cache["weather"]["data"]

def get_news():
    if cache["news"]["expires"] < datetime.now():
        try:
            feed = feedparser.parse(NEWS_FEED)
            headlines = [entry.title for entry in feed.entries[:3]]
            cache["news"] = {
                "data": headlines,
                "expires": datetime.now() + timedelta(hours=1),
            }
        except:
            pass
    return cache["news"]["data"]

def get_quote():
    if cache["quote"]["expires"] < datetime.now():
        try:
            r = requests.get(QUOTE_API).json()
            quote = r["contents"]["quotes"][0]["quote"]
        except:
            quote = "Heute ist ein guter Tag, etwas Neues zu lernen."
        cache["quote"] = {
            "data": quote,
            "expires": datetime.combine(datetime.now().date() + timedelta(days=1), datetime.min.time()),
        }
    return cache["quote"]["data"]

def get_date():
    if cache["date"]["expires"] < datetime.now():
        today = datetime.now().strftime("%A, %d. %B")
        cache["date"] = {
            "data": today,
            "expires": datetime.now() + timedelta(minutes=15),
        }
    return cache["date"]["data"]

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/data")
async def api_data():
    return JSONResponse({
        "time": datetime.now().strftime("%H:%M"),
        "date": get_date(),
        "weather": get_weather(),
        "news": get_news(),
        "quote": get_quote(),
    })
