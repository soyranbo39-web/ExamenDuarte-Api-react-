
from os import name
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from passlib.ifc import PasswordHash
from sqlalchemy.orm import Session

from app.api.v1.schemas import (
    CokiesOut,
    HeaderOut,
    Login,
    LoginIdentificadorOut,
    LoginResponde,
    Registro,
    SessionOut,
    TokenResponde,
)
from app.core.config import (
    AUTH_COOKIE_NAME,
    AUTH_COOKIE_SECURE,
    AUTH_TOKEN_EXPIRE_MINUTES,
    settings,
)
from app.core.db import get_db
from app.core.security import (
    create_access_token,
    get_auth_response,
    set_auth_cookie,
    verify_password,
)

from .repository import UserRepository

router = APIRouter(prefix="/auth", tags=["auth"])




#Login 
@router.post("/login",response_model=LoginResponde)
def login (
    payload: Login,
    response : Response,
    db : Annotated[Session,Depends(get_db)],
    query : Annotated[str , Query (
      title="Query de prueba",
      description="canto enpoind"
    )]
    ):
    
    repository = UserRepository(db) 
    user = repository.authenticate_user(payload.username,payload.password)
    if not user : 
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
            )

    token = create_access_token( 
        subject=user.id,
        expires_minutes=settings.AUTH_TOKEN_EXPIRE_MINUTES
    )
    
    #el token y la cokiee solo debe durar 3 minutos
    bearer_value = f"Bearer {token}"
    response.headers["Authorization"] = bearer_value
    max_age = settings.AUTH_TOKEN_EXPIRE_MINUTES * 3
    
    response.set_cookie( 
        key=settings.AUTH_COOKIE_NAME,
        value=token,
        httponly=settings.AUTH_COOKIE_HTTPONLY,
        secure=settings.AUTH_COOKIE_SECURE,
        samesite=settings.AUTH_COOKIE_SAMESITE,
        max_age=max_age,
        
    )
    return LoginResponde(
         body=TokenResponde(
            access_token=token,
            user=Login.model_validate(user)
        ),
        transports=LoginIdentificadorOut(
            header=HeaderOut(Authorization=bearer_value),
            cookie=CokiesOut(access_token=bearer_value)
        )
    )
    
    



