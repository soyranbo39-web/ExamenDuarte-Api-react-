
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Request, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.v1.schemas import (
    Login,
    LoginResponde,
)
from app.core.config import (
    settings,
)
from app.core.db import get_db
from app.core.security import create_access_token, get_password_hash

from ...models.auth import User
from .repository import UserRepository
from .schemas import Registro, UserOut

router = APIRouter(prefix="/auth", tags=["auth"])




@router.post("/login", response_model=LoginResponde)
def login(
    payload: Optional[Login] = None,
    response: Response = None,
    request: Request = None,
    db: Annotated[Session, Depends(get_db)] = None,
    autorizacion: Optional[str] = Header(None, alias="Authorization"),
):
    token, via_cookie = UserRepository.extract_token_and_origin(request, autorizacion)
    if token:
        user = UserRepository.decode_token_or_raise(token)
        return LoginResponde(
            user_id=user.id,
            username=user.username,
            authenticated=True,
            authenticated_via_cookie=via_cookie,
            token=token,
            cookie_name=settings.AUTH_COOKIE_NAME,
        )

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Credenciales no proporcionadas"
        )
    user = UserRepository(db).authenticate_user(payload.username, payload.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nombre de usuario o contraseña incorrectos"
        )
    token = create_access_token(data={"sub": str(user.username)})
    bearer_token = f"Bearer {token}"
    if response is not None:
        response.headers["Authorization"] = bearer_token
        response.set_cookie(
            key=settings.AUTH_COOKIE_NAME,
            value=bearer_token,
            httponly=settings.AUTH_COOKIE_HTTPONLY,
            secure=settings.AUTH_COOKIE_SECURE,
            samesite=settings.AUTH_COOKIE_SAMESITE,
            max_age=settings.AUTH_TOKEN_EXPIRE_MINUTES * 60,
            path="/"
        )
    return LoginResponde.from_user_and_token(user, token)
    

@router.post("/usuarios", status_code=status.HTTP_201_CREATED)
async def registrar_usuario(user: Registro, db: Annotated[Session, Depends(get_db)]):
    
    result = db.execute(select(User).where(User.username == user.username))
    existing_user = result.scalars().first()
    
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El nombre de usuario ya está registrado"
        )

    hashed_password = get_password_hash(user.password)

    new_user = User(
        name=user.full_name,
        username=user.username,
        password_hash=hashed_password
    
    )

    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return {"message": "Usuario creado exitosamente"}
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Hubo un fallo en la creación del usuario"
        )
    

@router.get("/user/me", response_model=UserOut)
async def read_users_me(
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    autorizacion: Optional[str] = Header(None, alias="Authorization"),
):
    token, _ = UserRepository.extract_token_and_origin(request, autorizacion)
    if not token:
        raise HTTPException(status_code=401, detail="No autorizado")
    username = UserRepository.decode_token_or_raise(token)
    user = UserRepository(db).get_by_user(username)
    if user is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return UserOut.model_validate(user)
    
    