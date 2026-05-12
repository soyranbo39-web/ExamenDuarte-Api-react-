import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.v1.router import router as auth_router
from app.core.config import DATABASE_URL
from app.core.db import Base, engine

load_dotenv()

def create_app() ->FastAPI: 
    app = FastAPI(title="Examen Canto es hermoso",version="1.0.0")
    Base.metadata.create_all(bind=engine)
    app.include_router(auth_router)

    return app

app = create_app()