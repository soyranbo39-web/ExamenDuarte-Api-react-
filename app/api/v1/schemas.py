#Modelos pydantic 
#Tenemos pensado que la cokkie dure una cantidad de tiempo 
from pydantic import BaseModel, Field

#Aqui estuvo canto 

class Registro (BaseModel):
    name : str = Field(min_length=1,max_length=100)
    username : str =  Field(min_length=1,max_length=50)
    password : str = Field(min_length=1, max_length= 100)

class Login(BaseModel):
    username : str
    password : str 

class CokiesOut(BaseModel):
    name: str
    http_only: bool
    secure: bool
    same_site: str
    max_age_seconds: int
 
class AuthOut(BaseModel):
     access_token : str
     token_type : str = "bearer"
     cookie : CokiesOut
     
class UserOut(BaseModel):
    id : str
    username : str
    username : str

class SessionOut(BaseModel):
    user_id: str
    authenticated: bool
    authenticated_via_cookie: bool
    cookie_name: str

    

