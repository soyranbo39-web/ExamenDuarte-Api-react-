
from typing import Optional,Annotated
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status 
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from app.core.config import AUTH_COOKIE_NAME,AUTH_COOKIE_SECURE,AUTH_TOKEN_EXPIRE_MINUTES
from app.api.v1.schemas import AuthOut,Registro,Login,UserOut,SessionOut,CokiesOut
from app.core.db import get_db
from app.core.config import settings
from .repository import UserRepository

router = APIRouter(prefix="/auth", tags=["auth"])
#cuando exista el repositori iria en esta parte 
repo = UserRepository() 



#Login 
@router.post("/login",response_model=AuthOut)
def login (from_data: Annotated[OAuth2PasswordRequestForm,Depends()],response : Response,db: Annotated[Session,Depends(get_db)]):
    repository = UserRepository(db)
    user = repository.authenticate_user(from_data.username,from_data.password)
    if not user : 
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
            )
    token = create_access_token(
        subject=user.id,
        expires_minutes=settings.AUTH_TOKEN_EXPIRE_MINUTES
    )
    #falta el header 
    
    #parte de la cookie
    max_age = settings.AUTH_TOKEN_EXPIRE_MINUTES * 60
    response.set_cookie( 
        key=settings.AUTH_COOKIE_NAME,
        value=token,
        httponly=settings.AUTH_COOKIE_HTTPONLY,
        secure=settings.AUTH_COOKIE_SECURE,
        samesite=settings.AUTH_COOKIE_SAMESITE,
        max_age=max_age,
        
    )
    return AuthOut(
        access_token=token,
        token_type="bearer",
        cookie=CokiesOut(
            name=settings.AUTH_COOKIE_NAME,
            http_only=settings.AUTH_COOKIE_HTTPONLY,
            secure=settings.AUTH_COOKIE_SECURE,
            same_site=settings.AUTH_COOKIE_SAMESITE,
            max_age_seconds=max_age
        )
    )
    
    



