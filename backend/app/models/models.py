from datetime import datetime
from sqlalchemy import String, Integer, Boolean, DateTime, ForeignKey, Text, Float, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.core.database import Base

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(20))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class Classroom(Base):
    __tablename__ = "classrooms"
    id: Mapped[int] = mapped_column(primary_key=True)
    teacher_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    name: Mapped[str] = mapped_column(String(120))
    description: Mapped[str] = mapped_column(Text, default="")
    class_code: Mapped[str] = mapped_column(String(16), unique=True, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    memberships = relationship("ClassroomStudent", back_populates="classroom", cascade="all, delete-orphan")

class ClassroomStudent(Base):
    __tablename__ = "classroom_students"
    __table_args__ = (UniqueConstraint("classroom_id", "student_id", name="uq_classroom_student"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    classroom_id: Mapped[int] = mapped_column(ForeignKey("classrooms.id"))
    student_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    joined_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    classroom = relationship("Classroom", back_populates="memberships")

class Dictation(Base):
    __tablename__ = "dictations"
    id: Mapped[int] = mapped_column(primary_key=True)
    classroom_id: Mapped[int] = mapped_column(ForeignKey("classrooms.id"))
    teacher_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    title: Mapped[str] = mapped_column(String(160))
    description: Mapped[str] = mapped_column(Text, default="")
    verified_text: Mapped[str] = mapped_column(Text)
    language: Mapped[str] = mapped_column(String(20), default="en")
    difficulty: Mapped[str] = mapped_column(String(20), default="medium")
    allow_replay: Mapped[bool] = mapped_column(Boolean, default=True)
    max_replays: Mapped[int] = mapped_column(Integer, default=3)
    status: Mapped[str] = mapped_column(String(20), default="published")
    audio_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class Attempt(Base):
    __tablename__ = "attempts"
    id: Mapped[int] = mapped_column(primary_key=True)
    dictation_id: Mapped[int] = mapped_column(ForeignKey("dictations.id"))
    student_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    submitted_image_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    extracted_text: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(30), default="started")
    ocr_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    needs_review: Mapped[bool] = mapped_column(Boolean, default=False)
    replay_count: Mapped[int] = mapped_column(Integer, default=0)
    pause_count: Mapped[int] = mapped_column(Integer, default=0)
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

class Score(Base):
    __tablename__ = "scores"
    id: Mapped[int] = mapped_column(primary_key=True)
    attempt_id: Mapped[int] = mapped_column(ForeignKey("attempts.id"), unique=True)
    overall_score: Mapped[float] = mapped_column(Float)
    word_accuracy: Mapped[float] = mapped_column(Float)
    character_accuracy: Mapped[float] = mapped_column(Float)
    spelling_errors: Mapped[int] = mapped_column(Integer)
    missing_words: Mapped[int] = mapped_column(Integer)
    extra_words: Mapped[int] = mapped_column(Integer)
    punctuation_errors: Mapped[int] = mapped_column(Integer)
    capitalization_errors: Mapped[int] = mapped_column(Integer)
    details_json: Mapped[str] = mapped_column(Text, default="[]")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
