
from os import name
from typing import Optional,Annotated
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status,Query
from passlib.ifc import PasswordHash
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from app.core.config import AUTH_COOKIE_NAME,AUTH_COOKIE_SECURE,AUTH_TOKEN_EXPIRE_MINUTES
from app.api.v1.schemas import Registro, Login,LoginResponde,LoginIdentificadorOut, CokiesOut, HeaderOut ,SessionOut,TokenResponde
from app.core.db import get_db
from app.core.config import settings
router = APIRouter(prefix="/auth", tags=["auth"])
#cuando exista el repositori iria en esta parte 
repo = UserRepository() 



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
    
    repository = UserRepository(db) # type: ignore
    user = repository.authenticate_user(payload.username,payload.password)
    if not user : 
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
            )

    token = create_access_token( # type: ignore
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
        transport=LoginIdentificadorOut(
            header=HeaderOut(Authorization=bearer_value), # type: ignore
            cookie=CokiesOut(access_token=bearer_value) # type: ignore
        )
       
    )
    
    



