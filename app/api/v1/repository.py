from sqlalchemy.orm import Session
from fastapi import HTTPException, Request ,status
import jwt
from app.models.auth import User
from app.core.config import settings
from app.core.security import verify_password, get_token_from_cookie, get_token_from_header, decode_token


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get(self, id_user : int) -> User | None:
        return self.db.get(User,id_user)
    
    def get_by_user (self, username : str) -> User | None:
       query = self.db.query(User).filter(User.username == username)
       return query.first()
        
    
    def create(self, user: str , password: str) -> User:
        new_user = User(
            name=user,
            username=user,
            password_hash=password
        )
        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)
        return new_user
    
    def authenticate_user(self, username: str, password: str) -> User | None:
        user = self.get_by_user(username)
        if not user:
            return None
        #se debera verificar el passwrod cuando exista el el security 
        if not verify_password(password, user.password_hash):
            return None
        return user
    
    def get_token(request: Request) -> str | None:
        token = get_token_from_cookie(request)
        
        if not token:
            auth_header = request.headers.get("Authorization")
            token = get_token_from_header(auth_header)
        
        return token    
   
    def decode(token_string: str):
        return decode_token(token_string)
    
    @staticmethod
    def extract_token_and_origin(request: Request, authorization: str | None):
        token = None
        authenticated_via_cookie = False
        
        if authorization and authorization.startswith("Bearer "):
            token = authorization.removeprefix("Bearer ").strip()
        else:
            cookie_value = request.cookies.get(settings.AUTH_COOKIE_NAME) if request else None
            if cookie_value:
                authenticated_via_cookie = True
                if cookie_value.startswith("Bearer "):
                    token = cookie_value.removeprefix("Bearer ").strip()
                else:
                    token = cookie_value.strip()
        
        return token, authenticated_via_cookie
    
    @staticmethod
    def decode_token_or_raise(token: str):
        try:
            payload_jwt = jwt.decode(
                token,
                settings.AUTH_SECRET_KEY.get_secret_value(),
                algorithms=[settings.AUTH_ALGORITHM],
            )
        except jwt.PyJWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido"
            )
        user_id = str(payload_jwt.get("sub", "")).strip()
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Payload de token inválido"
            )
        return user_id