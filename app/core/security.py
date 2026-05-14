from fastapi.security import OAuth2PasswordBearer
from fastapi import Response, HTTPException, Request, status, Depends
from pwdlib import PasswordHash
import jwt
from datetime import timedelta, datetime, timezone
from .config import settings
from ..api.v1.schemas import AuthOut, CokiesOut

password_hash = PasswordHash.recommended()
DUMMY_HASH = password_hash.hash("dummypassword")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_password_hash(password):
    return password_hash.hash(password)


def verify_password(plain_password, hashed_password):
    return password_hash.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.AUTH_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.AUTH_SECRET_KEY.get_secret_value(), 
        algorithm=settings.AUTH_ALGORITHM
    )
    return encoded_jwt

def set_auth_cookie(response: Response, user_id: int):
    token = create_access_token(data={"sub": str(user_id)})
    
    response.set_cookie(
        key=settings.AUTH_COOKIE_NAME,
        value=f"Bearer {token}",
        httponly=settings.AUTH_COOKIE_HTTPONLY,
        secure=settings.AUTH_COOKIE_SECURE,
        samesite=settings.AUTH_COOKIE_SAMESITE,
        max_age=settings.AUTH_TOKEN_EXPIRE_MINUTES * 60,
        path="/"
    )
    return token

def get_auth_response(token: str) -> AuthOut:
    return AuthOut(
        access_token=token,
        token_type="bearer",
        cookie=CokiesOut(
            name=settings.AUTH_COOKIE_NAME,
            http_only=settings.AUTH_COOKIE_HTTPONLY,
            secure=settings.AUTH_COOKIE_SECURE,
            same_site=settings.AUTH_COOKIE_SAMESITE,
            max_age_seconds=settings.AUTH_TOKEN_EXPIRE_MINUTES * 60
        )
    )

def get_token_from_cookie(request: Request) -> str:
    token = request.cookies.get(settings.AUTH_COOKIE_NAME)
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No se encontró la cookie de sesión"
        )
    
    if token.startswith("Bearer "):
        return token.replace("Bearer ", "")
        
    return token

def get_token_from_header(token: str = Depends(oauth2_scheme)) -> str:
    return token