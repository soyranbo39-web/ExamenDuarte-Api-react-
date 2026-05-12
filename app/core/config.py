
import os
from pathlib import Path

# DATOS PARA LA BASE DE SQLITE
BASE_DIR = Path(__file__).resolve().parents[2]
SQLITE_DB_PATH = BASE_DIR / "data" / "CantoEstaHermoso"
DATABASE_URL = f"sqlite:///{SQLITE_DB_PATH}"