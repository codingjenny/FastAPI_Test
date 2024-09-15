from sqlalchemy import Column, Integer, String, ForeignKey, LargeBinary, DateTime, Enum
from sqlalchemy.orm import relationship
from .database import Base
import enum
from datetime import datetime

class StatusEnum(str, enum.Enum):
    Success = "Success"
    Fail = "Fail"

class User(Base):
    __tablename__ = "User"
    
    idUser = Column(Integer, primary_key=True, index=True, autoincrement=True)
    UserName = Column(String(45), unique=True, index=True, nullable=False)
    Password = Column(String(100), nullable=False)
    
    uploads = relationship("UploadFile", back_populates="user")

class UploadFile(Base):
    __tablename__ = "UploadFile"
    
    idUploadFile = Column(Integer, primary_key=True, index=True, autoincrement=True)
    idUser = Column(Integer, ForeignKey("User.idUser"), nullable=False)
    FileName = Column(String(45), nullable=False)
    UploadTime = Column(DateTime, default=datetime.utcnow, nullable=False)
    Status = Column(Enum(StatusEnum), nullable=False)
    ZipFile = Column(LargeBinary, nullable=False)

    user = relationship("User", back_populates="uploads")
