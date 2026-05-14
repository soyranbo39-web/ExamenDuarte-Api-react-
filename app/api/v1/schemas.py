#Modelos pydantic 
#Tenemos pensado que la cokkie dure una cantidad de tiempo 
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field
# ya me arte de estar cambiando odio las cookies y los headers
#Aqui estuvo canto. Ya canto se vino a qui 

class Registro(BaseModel):
    full_name: str = Field(min_length=1,max_length=100)
    username : str =  Field(min_length=1,max_length=50)
    password : str = Field(min_length=1, max_length= 100)
    model_config = ConfigDict(from_attributes=True)
    
class Login(Registro):
    username: str
    password: str
    full_name: Optional[str] = None

class UserOut(BaseModel):
    id: int
    username: str
    full_name: str = Field(alias="name")
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

class SessionOut(BaseModel):
    user_id: str
    authenticated: bool
    authenticated_via_cookie: bool
    cookie_name: str

class TokenResponde(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user : UserOut


class CokiesOut(BaseModel):
    access_token: str
    token_type: Literal["bearer"] = "bearer"
      

class HeaderOut(BaseModel):
    authorization: str = Field(..., alias="Authorization")
    model_config = ConfigDict(populate_by_name=True)

class LoginIdentificadorOut(BaseModel):
    header: HeaderOut
    cookie: CokiesOut

class LoginResponde(BaseModel):
    body: TokenResponde
    transports : LoginIdentificadorOut
    @classmethod
    def from_user_and_token(cantomelastimas, user, token: str):
        bearer = f"Bearer {token}"
        return cantomelastimas(
            body=TokenResponde(
                access_token=token,
                user=UserOut.model_validate(user),
            ),
            transports=LoginIdentificadorOut(
                header=HeaderOut(Authorization=bearer),
                cookie=CokiesOut(access_token=bearer),
            ),
        )
    
    


    

    

    

