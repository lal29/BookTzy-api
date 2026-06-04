from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import get_db
from models import Appointment

router = APIRouter(prefix="/api", tags=["locations"])


@router.get("/locations")
def get_locations(db: Session = Depends(get_db)):
    return {
        "locations": [
            {"name": "Surrey", "address": "123 King George Blvd"},
            {"name": "Vancouver", "address": "456 Granville St"},
        ]
    }
