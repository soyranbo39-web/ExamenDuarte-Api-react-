from fastapi import FastAPI
from fastapi.concurrency import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

load_dotenv()
localhost_url = os.getenv("LOCALHOST")
ip_direction_url = os.getenv("IP_DIRECTION")

origins = [
    localhost_url,
    ip_direction_url
]

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan, separate_input_output_schemas=False)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
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
