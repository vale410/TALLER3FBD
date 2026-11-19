
import os
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from bson import ObjectId

app = FastAPI(title="DrinkAdvisor API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"]
)

MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB", "DRINKADVISOR")

if not MONGO_URI:
    raise RuntimeError("Falta configurar MONGO_URI")

client = MongoClient(MONGO_URI)
db = client[MONGO_DB]


def convertir_documento(doc):
    doc["_id"] = str(doc["_id"])
    return doc


@app.get("/")
def inicio():
    return {"mensaje": "API DrinkAdvisor funcionando"}


@app.get("/bares/{bar_id}/comentarios")
def obtener_comentarios(bar_id: int):
    comentarios = db.comentarios_bares.find({"bar_id": bar_id})
    return [convertir_documento(c) for c in comentarios]


@app.post("/bares/{bar_id}/comentarios")
def crear_comentario(bar_id: int, datos: dict):
    comentario = dict(datos)
    comentario["bar_id"] = bar_id
    comentario["date"] = datetime.now(timezone.utc)

    calificacion = comentario.get("calificacion")
    if calificacion is not None:
        if type(calificacion) is not int or not 1 <= calificacion <= 5:
            raise HTTPException(
                status_code=400,
                detail="La calificacion debe estar entre 1 y 5"
            )

    resultado = db.comentarios_bares.insert_one(comentario)
    return {"mensaje": "Comentario creado", "id": str(resultado.inserted_id)}


@app.get("/bares/{bar_id}/eventos")
def obtener_eventos(bar_id: int):
    eventos = db.eventos.find({"bar_id": bar_id})
    return [convertir_documento(e) for e in eventos]


@app.post("/bares/{bar_id}/eventos")
def crear_evento(bar_id: int, datos: dict):
    evento = dict(datos)

    if not isinstance(evento.get("nombre"), str) or not evento["nombre"].strip():
        raise HTTPException(
            status_code=400,
            detail="El nombre del evento es obligatorio"
        )

    evento["bar_id"] = bar_id
    evento["fecha_creacion"] = datetime.now(timezone.utc)

    resultado = db.eventos.insert_one(evento)
    return {"mensaje": "Evento creado", "id": str(resultado.inserted_id)}
