#Modelos pydantic 
#Tenemos pensado que la cokkie dure una cantidad de tiempo 
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field


#Aqui estuvo canto. Ya canto se vino a qui 

class Registro(BaseModel):
    full_name: str = Field(min_length=1,max_length=100)
    username : str =  Field(min_length=1,max_length=50)
    password : str = Field(min_length=1, max_length= 100)
    model_config = ConfigDict(from_attributes=True)
    
    
class Login(Registro):
    id : int 
    is_active : bool

class TokenResponde(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user : Login


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
    

class SessionOut(BaseModel):
    user_id: str
    authenticated: bool
    authenticated_via_cookie: bool
    cookie_name: str
    

