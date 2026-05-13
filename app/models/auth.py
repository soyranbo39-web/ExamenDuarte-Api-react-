from datetime import datetime
from typing import Literal
from sqlalchemy import Boolean, DateTime, Enum, String,func
from sqlalchemy.orm import Mapped, mapped_column
from app.core.db import Base

# se debera llamas a core.db


class User(Base):
    __tablename__ = "Users"
    
    id : Mapped [int] = mapped_column(String(50),primary_key=True)
    name : Mapped[str] = mapped_column(String(100),nullable=False)
    username: Mapped[str] = mapped_column(String(50),nullable=False,unique=True,index=True)
    password_hash :Mapped[str]= mapped_column(String(100),unique=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        
    )
    
    



