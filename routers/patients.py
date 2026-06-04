from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import User, Appointment
from security import get_current_user

router = APIRouter(prefix="/api/patients", tags=["patients"])


@router.get("/me")
def get_my_profile(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "email": current_user.email,
        "role": current_user.role,
        "member_since": current_user.created_at,
    }


@router.get("/my-appointments")
def get_my_appointments(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    appointments = (
        db.query(Appointment).filter(Appointment.patient_id == current_user.id).all()
    )

    return {
        "patient": current_user.first_name,
        "total": len(appointments),
        "appointments": [
            {
                "id": a.id,
                "service_id": a.service_id,
                "location": a.location,
                "datetime": a.appointment_datetime,
                "status": a.status.value,
            }
            for a in appointments
        ],
    }
