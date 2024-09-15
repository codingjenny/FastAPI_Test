from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum

##################
class StatusEnum(str, Enum):
    Success = "Success"
    Fail = "Fail"
##################


##################
class UserCreate(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    idUser: int
    username: str

    class Config:
        from_attributes = True
##################


##################
class UploadFileResponse(BaseModel):
    idUploadFile: int
    filename: str
    upload_time: datetime
    status: StatusEnum

    class Config:
        from_attributes = True
##################


##################
class TokenData(BaseModel):
    username: Optional[str] = None

class User(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
##################



