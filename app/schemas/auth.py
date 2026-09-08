from pydantic import BaseModel, Field, EmailStr, ConfigDict
from datetime import datetime


class UserSignUp(BaseModel):
    name : str
    email : EmailStr
    password : str
    organization_name : str
    
    model_config = ConfigDict(str_strip_whitespace=True)

class UserLogin(BaseModel):
    email : str
    password : str
    
class TokenResponse(BaseModel):
    access_token: str
    token_type: str