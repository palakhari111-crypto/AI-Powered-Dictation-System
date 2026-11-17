from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.core.security import hash_password, verify_password, create_access_token, get_current_user
from backend.app.models.models import User
from backend.app.schemas.schemas import RegisterIn, LoginIn

router = APIRouter()

@router.post("/register")
def register(payload: RegisterIn, db: Session = Depends(get_db)):
    if payload.role not in ("teacher", "student"):
        raise HTTPException(400, "Role must be teacher or student")
    email = payload.email.lower()
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(409, "Email already registered")
    user = User(name=payload.name.strip(), email=email, password_hash=hash_password(payload.password), role=payload.role)
    db.add(user); db.commit(); db.refresh(user)
    return {"id": user.id, "name": user.name, "email": user.email, "role": user.role}

@router.post("/login")
def login(payload: LoginIn, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email.lower()).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(401, "Incorrect email or password")
    return {"access_token": create_access_token(user.id), "token_type": "bearer",
            "user": {"id": user.id, "name": user.name, "email": user.email, "role": user.role}}

@router.get("/me")
def me(user: User = Depends(get_current_user)):
    return {"id": user.id, "name": user.name, "email": user.email, "role": user.role}
