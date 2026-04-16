from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import Note
from ..schemas import NoteCreate, NoteUpdate, NoteOut

router = APIRouter(prefix="/notes", tags=["notes"])


@router.get("/", response_model=List[NoteOut])
def list_notes(category: str = None, db: Session = Depends(get_db)):
    query = db.query(Note)
    if category:
        query = query.filter(Note.category == category)
    return query.order_by(Note.created_at.desc()).all()


@router.post("/", response_model=NoteOut)
def create_note(note: NoteCreate, db: Session = Depends(get_db)):
    db_note = Note(**note.model_dump())
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    return db_note


@router.put("/{note_id}", response_model=NoteOut)
def update_note(note_id: int, note: NoteUpdate, db: Session = Depends(get_db)):
    db_note = db.query(Note).filter(Note.id == note_id).first()
    if not db_note:
        raise HTTPException(status_code=404, detail="Nota não encontrada")
    for field, value in note.model_dump(exclude_unset=True).items():
        setattr(db_note, field, value)
    db.commit()
    db.refresh(db_note)
    return db_note


@router.delete("/{note_id}")
def delete_note(note_id: int, db: Session = Depends(get_db)):
    db_note = db.query(Note).filter(Note.id == note_id).first()
    if not db_note:
        raise HTTPException(status_code=404, detail="Nota não encontrada")
    db.delete(db_note)
    db.commit()
    return {"ok": True}
