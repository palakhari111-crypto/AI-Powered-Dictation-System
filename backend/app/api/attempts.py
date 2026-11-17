from datetime import datetime
from pathlib import Path
import uuid, json
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.core.config import settings
from backend.app.core.security import get_current_user, require_role
from backend.app.models.models import User, Dictation, ClassroomStudent, Attempt, Score, Classroom
from backend.app.services.ocr_service import extract_text
from backend.app.services.evaluation_service import evaluate

router = APIRouter()
ALLOWED = {"image/jpeg", "image/png"}

@router.post("/start/{dictation_id}")
def start_attempt(dictation_id: int, db: Session = Depends(get_db), user: User = Depends(require_role("student"))):
    d = db.query(Dictation).filter_by(id=dictation_id, status="published").first()
    if not d: raise HTTPException(404, "Dictation not found")
    if not db.query(ClassroomStudent).filter_by(classroom_id=d.classroom_id, student_id=user.id).first():
        raise HTTPException(403, "Join the classroom before attempting this dictation")
    a = Attempt(dictation_id=d.id, student_id=user.id)
    db.add(a); db.commit(); db.refresh(a)
    return {"attempt_id": a.id, "started_at": a.started_at.isoformat()}

@router.post("/{attempt_id}/submission")
async def submit(attempt_id: int, image: UploadFile = File(...), db: Session = Depends(get_db), user: User = Depends(require_role("student"))):
    a = db.query(Attempt).filter_by(id=attempt_id, student_id=user.id).first()
    if not a: raise HTTPException(404, "Attempt not found")
    if a.status == "completed": raise HTTPException(409, "Attempt already submitted")
    if image.content_type not in ALLOWED: raise HTTPException(415, "Upload a JPG or PNG image")
    content = await image.read()
    if len(content) > 8 * 1024 * 1024: raise HTTPException(413, "Image must be 8 MB or smaller")
    folder = Path(settings.UPLOAD_DIR); folder.mkdir(parents=True, exist_ok=True)
    suffix = ".png" if image.content_type == "image/png" else ".jpg"
    path = folder / f"attempt_{attempt_id}_{uuid.uuid4().hex}{suffix}"
    path.write_bytes(content)
    result = extract_text(str(path))
    a.submitted_image_path = str(path)
    a.extracted_text = result.text
    a.ocr_confidence = result.confidence
    a.needs_review = result.needs_review
    a.submitted_at = datetime.utcnow()
    a.status = "needs_review" if result.needs_review else "completed"
    db.commit()
    d = db.query(Dictation).filter_by(id=a.dictation_id).first()
    evaluation = evaluate(d.verified_text, result.text) if result.text else None
    if evaluation:
        score = Score(attempt_id=a.id, overall_score=evaluation["overall_score"],
            word_accuracy=evaluation["word_accuracy"], character_accuracy=evaluation["character_accuracy"],
            spelling_errors=evaluation["spelling_errors"], missing_words=evaluation["missing_words"],
            extra_words=evaluation["extra_words"], punctuation_errors=evaluation["punctuation_errors"],
            capitalization_errors=evaluation["capitalization_errors"], details_json=json.dumps(evaluation["details"]))
        db.add(score); db.commit()
    return {"attempt_id": a.id, "extracted_text": result.text, "ocr_confidence": result.confidence,
            "needs_review": result.needs_review, "ocr_message": result.message, "evaluation": evaluation}

@router.get("/{attempt_id}/report")
def report(attempt_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    a = db.query(Attempt).filter_by(id=attempt_id).first()
    if not a: raise HTTPException(404, "Attempt not found")
    d = db.query(Dictation).filter_by(id=a.dictation_id).first()
    if user.role == "student" and a.student_id != user.id: raise HTTPException(403, "Forbidden")
    if user.role == "teacher" and d.teacher_id != user.id: raise HTTPException(403, "Forbidden")
    s = db.query(Score).filter_by(attempt_id=a.id).first()
    return {"attempt_id": a.id, "dictation_title": d.title, "status": a.status,
            "extracted_text": a.extracted_text, "ocr_confidence": a.ocr_confidence,
            "needs_review": a.needs_review,
            "score": None if not s else {"overall_score": s.overall_score, "word_accuracy": s.word_accuracy,
                "character_accuracy": s.character_accuracy, "spelling_errors": s.spelling_errors,
                "missing_words": s.missing_words, "extra_words": s.extra_words,
                "punctuation_errors": s.punctuation_errors, "capitalization_errors": s.capitalization_errors,
                "details": json.loads(s.details_json)}}

@router.get("/classroom/{classroom_id}/summary")
def classroom_summary(classroom_id: int, db: Session = Depends(get_db), user: User = Depends(require_role("teacher"))):
    c = db.query(Classroom).filter_by(id=classroom_id, teacher_id=user.id).first()
    if not c: raise HTTPException(404, "Classroom not found")
    dictation_ids = [d.id for d in db.query(Dictation).filter_by(classroom_id=c.id).all()]
    attempts = db.query(Attempt).filter(Attempt.dictation_id.in_(dictation_ids)).all() if dictation_ids else []
    result = []
    for a in attempts:
        student = db.query(User).filter_by(id=a.student_id).first()
        score = db.query(Score).filter_by(attempt_id=a.id).first()
        result.append({"student": student.name if student else "Unknown", "attempt_id": a.id,
                       "status": a.status, "score": score.overall_score if score else None})
    return result
