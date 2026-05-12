import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# DATOS PARA LA BASE DE SQLITE
BASE_DIR = Path(__file__).resolve().parents[2]
SQLITE_DB_PATH = BASE_DIR / "data" / "CantoEstaHermoso"
DATABASE_URL = f"sqlite:///{SQLITE_DB_PATH}"

#galleta
AUTH_COOKIE_NAME = os.getenv("AUTH_COOKIE_NAME")
AUTH_COOKIE_SECURE = os.getenv("AUTH_COOKIE_SECURE").lower() == "true"

#token
ALGORITHM = os.getenv("ALGORITHM")
if not ALGORITHM:
  raise RuntimeError("ALGORYTHM no encontrado en el entorno")
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
  raise RuntimeError("SECRET_KEY no encontrada en el entorno")
AUTH_TOKEN_EXPIRE_MINUTES = int(os.getenv("AUTH_TOKEN_EXPIRE_MINUTES"))
if not AUTH_TOKEN_EXPIRE_MINUTES:
  raise RuntimeError("AUTH_TOKEN_EXPIRE_MINUTES no encontrada en el entorno")
    