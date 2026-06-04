from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import Service

router = APIRouter(prefix="/api/services", tags=["services"])


@router.get("")
def get_all_services(db: Session = Depends(get_db)):
    all_services = db.query(Service).all()

    return {
        "services": [
            {
                "id": s.id,
                "name": s.name,
                "duration_minutes": s.duration_minutes,
                "description": s.description,
            }
            for s in all_services
        ]
    }
