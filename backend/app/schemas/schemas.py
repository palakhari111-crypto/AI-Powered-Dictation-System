from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class RegisterIn(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)
    role: str

class LoginIn(BaseModel):
    email: EmailStr
    password: str

class ClassroomIn(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    description: str = ""

class JoinIn(BaseModel):
    class_code: str

class DictationIn(BaseModel):
    classroom_id: int
    title: str
    description: str = ""
    text: str = Field(min_length=1, max_length=12000)
    language: str = "en"
    difficulty: str = "medium"
    allow_replay: bool = True
    max_replays: int = 3
