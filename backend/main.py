from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from backend.recomendador import recomendar_destinos
from backend.auth import router as auth_router
from backend.database import crear_base_datos
from backend.uso import obtener_uso, incrementar_uso

import sqlite3
import os

# 👉 Rutas
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "..", "travel_ai.db")

# 👉 Templates
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

app = FastAPI(title="Travel AI API")

crear_base_datos()
app.include_router(auth_router)

# 👉 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 👉 FRONTEND PRINCIPAL
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# 🔥 PLAN
def obtener_plan(email):
    conexion = sqlite3.connect(DB_PATH)
    cursor = conexion.cursor()

    cursor.execute("SELECT plan FROM usuarios WHERE email=?", (email,))
    resultado = cursor.fetchone()

    conexion.close()

    if resultado:
        return resultado[0]
    return "free"


# 👉 API
@app.get("/recomendar")
def recomendar(presupuesto: int, tipo: str, email: str = "demo@demo.com"):

    plan = obtener_plan(email)

    if plan == "free":
        uso_actual = obtener_uso(email)

        if uso_actual >= 3:
            return {"error": "Has alcanzado el límite FREE (3 consultas). Pásate a PRO 🚀"}

        incrementar_uso(email)

        resultados = recomendar_destinos(presupuesto, tipo)

        return {
            "plan": "free",
            "consultas_usadas": uso_actual + 1,
            "recomendaciones": resultados
        }

    resultados = recomendar_destinos(presupuesto, tipo)

    return {
        "plan": "pro",
        "recomendaciones": resultados
    }