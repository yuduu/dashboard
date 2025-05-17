import os
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from datetime import date

BASE_DIR = Path(__file__).resolve().parent

# This is the fix: mount app under a proxy path
root_path = os.getenv("ROOT_PATH", "")

app = FastAPI(root_path=root_path)
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/date", response_class=HTMLResponse)
async def get_date():
    today = date.today().strftime("%A, %d %B %Y")
    return HTMLResponse(content=f"<div>{today}</div>")
