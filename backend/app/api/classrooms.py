import secrets, string
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.core.security import get_current_user, require_role
from backend.app.models.models import User, Classroom, ClassroomStudent, Dictation
from backend.app.schemas.schemas import ClassroomIn, JoinIn

router = APIRouter()

def make_code(db):
    alphabet = string.ascii_uppercase + string.digits
    for _ in range(20):
        code = "".join(secrets.choice(alphabet) for _ in range(7))
        if not db.query(Classroom).filter_by(class_code=code).first():
            return code
    raise HTTPException(500, "Could not generate classroom code")

@router.post("")
def create_classroom(payload: ClassroomIn, db: Session = Depends(get_db), user: User = Depends(require_role("teacher"))):
    c = Classroom(teacher_id=user.id, name=payload.name, description=payload.description, class_code=make_code(db))
    db.add(c); db.commit(); db.refresh(c)
    return {"id": c.id, "name": c.name, "description": c.description, "class_code": c.class_code}

@router.get("")
def list_classrooms(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if user.role == "teacher":
        rows = db.query(Classroom).filter_by(teacher_id=user.id, is_active=True).all()
    else:
        ids = [m.classroom_id for m in db.query(ClassroomStudent).filter_by(student_id=user.id).all()]
        rows = db.query(Classroom).filter(Classroom.id.in_(ids), Classroom.is_active == True).all() if ids else []
    return [{"id": c.id, "name": c.name, "description": c.description, "class_code": c.class_code} for c in rows]

@router.post("/join")
def join_classroom(payload: JoinIn, db: Session = Depends(get_db), user: User = Depends(require_role("student"))):
    c = db.query(Classroom).filter_by(class_code=payload.class_code.strip().upper(), is_active=True).first()
    if not c: raise HTTPException(404, "Invalid classroom code")
    existing = db.query(ClassroomStudent).filter_by(classroom_id=c.id, student_id=user.id).first()
    if existing: raise HTTPException(409, "You already joined this classroom")
    db.add(ClassroomStudent(classroom_id=c.id, student_id=user.id)); db.commit()
    return {"message": "Joined classroom", "classroom_id": c.id, "name": c.name}

@router.get("/{classroom_id}/students")
def classroom_students(classroom_id: int, db: Session = Depends(get_db), user: User = Depends(require_role("teacher"))):
    c = db.query(Classroom).filter_by(id=classroom_id, teacher_id=user.id).first()
    if not c: raise HTTPException(404, "Classroom not found")
    rows = db.query(ClassroomStudent, User).join(User, User.id == ClassroomStudent.student_id).filter(ClassroomStudent.classroom_id == c.id).all()
    return [{"id": u.id, "name": u.name, "email": u.email} for _, u in rows]
