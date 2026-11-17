from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.core.database import Base, engine
from backend.app.core.config import settings
from backend.app.api import auth, classrooms, dictations, attempts

Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.APP_NAME, version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501", "http://127.0.0.1:8501"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(classrooms.router, prefix="/classrooms", tags=["Classrooms"])
app.include_router(dictations.router, prefix="/dictations", tags=["Dictations"])
app.include_router(attempts.router, prefix="/attempts", tags=["Attempts"])

@app.get("/")
def root():
    return {"message": "AI-Powered Dictation API is running", "docs": "/docs"}

@app.get("/health")
def health():
    return {"status": "ok"}
