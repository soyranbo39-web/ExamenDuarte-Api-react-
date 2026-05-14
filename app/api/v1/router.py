
from multiprocessing import AuthenticationError
from os import name
from tokenize import cookie_re
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Header, Query, Request, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from passlib.ifc import PasswordHash
from sqlalchemy.orm import Session
from sqlalchemy import select
from ...models.auth import User
from .schemas import Registro

from app.api.v1.schemas import (
    Login,
    LoginResponde,
    SessionOut,

)
from app.core.config import (
    settings,
)
from app.core.db import get_db
from app.core.security import (
    create_access_token,
    get_password_hash
)

from .repository import UserRepository

router = APIRouter(prefix="/auth", tags=["auth"])





#Login 
@router.post("/login",response_model=LoginResponde)
def login (
    payload: Optional[Login] = None,
    response : Response= None,
    request : Request=None,
    db : Annotated[Session,Depends(get_db)] = None,
    autorizacion : Optional[str]=Header(None,alias="Authorization"),
    ):
    token = None 
    autentificaciom_via_cookie = False
    
    if autorizacion and autorizacion.startswith("Bearer "):
        token = autorizacion.removeprefix("Bearer ").strip()
    
    else :
        cookie_value = request.cookies.get(settings.AUTH_COOKIE_NAME) if request else None
        if cookie_value:
            autentificaciom_via_cookie = True
            if cookie_value.startswith("Bearer "):
                token = cookie_value.removeprefix("Bearer ").strip()
            else:
                token = cookie_value.strip()
    
    if token: 
        try: 
            paload_jwt = jwt.decode(
                token, 
                settings.AUTH_SECRET_KEY.get_secret_value(), 
                algorithms=[settings.AUTH_ALGORITHM]
                )
        except jwt.PyJWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido"
            )
        user_id= str(paload_jwt.get("sub").strip())
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Payload de token inválido"
            )
        return SessionOut(
            user_id=user_id,
            authenticated=True,
            authenticated_via_cookie=autentificaciom_via_cookie,
            cookie_name=settings.AUTH_COOKIE_NAME if autentificaciom_via_cookie else None
        )
        
    repository = UserRepository(db) 
    user = repository.authenticate_user(payload.username,payload.password)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username y password son requeridos"
        )
    
    
    if not user : 
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas"
            )
    
    token = create_access_token(data={"sub": str(user.id)})
    
    #el token y la cokiee solo debe durar 3 minutos
    bearer_value = f"Bearer {token}"
    response.headers["Authorization"] = bearer_value
    
    response.set_cookie( 
        key=settings.AUTH_COOKIE_NAME,
        value=bearer_value,
        httponly=settings.AUTH_COOKIE_HTTPONLY,
        secure=settings.AUTH_COOKIE_SECURE,
        samesite=settings.AUTH_COOKIE_SAMESITE,
        max_age=settings.AUTH_TOKEN_EXPIRE_MINUTES * 60,
        path="/"
        
    )
    return LoginResponde.from_user_and_token(user, token)

@router.post("/usuarios", status_code=status.HTTP_201_CREATED)
async def registrar_usuario(user: Registro, db: Session = Depends(get_db)):
    existing_user = db.exec(
        select(User).where(User.username == user.username)
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El nombre de usuario ya está registrado"
        )

    hashed_password = get_password_hash(user.password)

    new_user = User(
        full_name=user.full_name,
        username=user.username,
        password=hashed_password
    )

    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        return {"message": "Usuario creado exitosamente"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Hubo un fallo en la creación del usuario"
        )
    
@router.get("/users/me")
async def read_users_me(request: Request, db: Session = Depends(get_db)):
    repository = UserRepository(db)
    token_string = repository.get_token(request)
    if not token_string:
        raise HTTPException(status_code=401, detail="No autorizado")

    payload = repository.decode(token_string)
    if not payload or not payload.get("sub"):
        raise HTTPException(status_code=401, detail="Token expirado o inválido")

    username = payload.get("sub")
    user = db.exec(select(User).where(User.username == username)).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    return user
    



