from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from ..database import get_db
from ..models import Finance
from ..schemas import FinanceCreate, FinanceOut

router = APIRouter(prefix="/finance", tags=["finance"])


@router.get("/", response_model=List[FinanceOut])
def list_entries(db: Session = Depends(get_db)):
    return db.query(Finance).order_by(Finance.date.desc(), Finance.created_at.desc()).all()


@router.get("/summary")
def get_summary(db: Session = Depends(get_db)):
    income = db.query(func.sum(Finance.amount)).filter(Finance.type == "income").scalar() or 0
    expense = db.query(func.sum(Finance.amount)).filter(Finance.type == "expense").scalar() or 0
    return {"income": income, "expense": expense, "balance": income - expense}


@router.post("/", response_model=FinanceOut)
def create_entry(entry: FinanceCreate, db: Session = Depends(get_db)):
    db_entry = Finance(**entry.model_dump())
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    return db_entry


@router.delete("/{entry_id}")
def delete_entry(entry_id: int, db: Session = Depends(get_db)):
    db_entry = db.query(Finance).filter(Finance.id == entry_id).first()
    if not db_entry:
        raise HTTPException(status_code=404, detail="Lançamento não encontrado")
    db.delete(db_entry)
    db.commit()
    return {"ok": True}
