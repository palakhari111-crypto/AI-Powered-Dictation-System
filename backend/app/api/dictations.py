from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.core.security import get_current_user, require_role
from backend.app.models.models import User, Classroom, ClassroomStudent, Dictation
from backend.app.schemas.schemas import DictationIn
from backend.app.services.tts_service import generate_audio

router = APIRouter()

@router.post("")
def create_dictation(payload: DictationIn, db: Session = Depends(get_db), user: User = Depends(require_role("teacher"))):
    classroom = db.query(Classroom).filter_by(id=payload.classroom_id, teacher_id=user.id).first()
    if not classroom: raise HTTPException(404, "Classroom not found or not owned by you")
    d = Dictation(classroom_id=classroom.id, teacher_id=user.id, title=payload.title,
                  description=payload.description, verified_text=payload.text.strip(),
                  language=payload.language, difficulty=payload.difficulty,
                  allow_replay=payload.allow_replay, max_replays=max(0, payload.max_replays))
    db.add(d); db.commit(); db.refresh(d)
    return {"id": d.id, "title": d.title, "status": d.status}

@router.get("")
def list_dictations(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if user.role == "teacher":
        rows = db.query(Dictation).filter_by(teacher_id=user.id).all()
    else:
        classroom_ids = [m.classroom_id for m in db.query(ClassroomStudent).filter_by(student_id=user.id).all()]
        rows = db.query(Dictation).filter(Dictation.classroom_id.in_(classroom_ids), Dictation.status == "published").all() if classroom_ids else []
    return [{"id": d.id, "classroom_id": d.classroom_id, "title": d.title, "description": d.description,
             "difficulty": d.difficulty, "language": d.language, "audio_available": bool(d.audio_path)} for d in rows]

@router.post("/{dictation_id}/generate-audio")
def audio(dictation_id: int, db: Session = Depends(get_db), user: User = Depends(require_role("teacher"))):
    d = db.query(Dictation).filter_by(id=dictation_id, teacher_id=user.id).first()
    if not d: raise HTTPException(404, "Dictation not found")
    try:
        d.audio_path = generate_audio(d.verified_text, d.language, f"dictation_{d.id}.mp3")
        db.commit()
        return {"message": "Audio generated", "audio_available": True}
    except Exception as exc:
        raise HTTPException(503, f"Audio generation failed. Check internet and language settings. ({type(exc).__name__})")

@router.get("/{dictation_id}")
def get_dictation(dictation_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    d = db.query(Dictation).filter_by(id=dictation_id).first()
    if not d: raise HTTPException(404, "Dictation not found")
    if user.role == "teacher":
        if d.teacher_id != user.id: raise HTTPException(403, "Forbidden")
    else:
        membership = db.query(ClassroomStudent).filter_by(classroom_id=d.classroom_id, student_id=user.id).first()
        if not membership or d.status != "published": raise HTTPException(403, "Forbidden")
    return {"id": d.id, "title": d.title, "description": d.description, "text": d.verified_text if user.role == "teacher" else None,
            "audio_available": bool(d.audio_path), "allow_replay": d.allow_replay, "max_replays": d.max_replays}

@router.get("/{dictation_id}/audio")
def get_audio(dictation_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    from fastapi.responses import FileResponse
    d = db.query(Dictation).filter_by(id=dictation_id).first()
    if not d or not d.audio_path: raise HTTPException(404, "Audio not available")
    if user.role == "teacher" and d.teacher_id != user.id: raise HTTPException(403, "Forbidden")
    if user.role == "student" and not db.query(ClassroomStudent).filter_by(classroom_id=d.classroom_id, student_id=user.id).first(): raise HTTPException(403, "Forbidden")
    return FileResponse(d.audio_path, media_type="audio/mpeg", filename=f"dictation_{d.id}.mp3")
