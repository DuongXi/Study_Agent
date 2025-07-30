from sqlalchemy import Column, Integer, String, Text, DateTime
from pydantic import BaseModel
from src.database import Base
from datetime import datetime, timezone

class Message(BaseModel):
    message: str

class Model(BaseModel):
    model: str
    
class Query(BaseModel):
    query: str

class Feedback(BaseModel):
    user_email: str
    message: str

class TokenInfo(BaseModel):
    user_email: str
    access_token: str
    refresh_token: str
    expires_at: str
    
class CookieToken(BaseModel):
    user_email: str
    access_token: str

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    access_token = Column(Text)
    refresh_token = Column(Text)
    expires_at = Column(DateTime)
    
class Feedback(Base):
    __tablename__ = "feedbacks"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, index=True)
    message = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))

class FeedbackInput(BaseModel):
    email: str
    message: str