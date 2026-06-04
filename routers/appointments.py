from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from pydantic import BaseModel
from datetime import datetime, timedelta
from database import get_db
from models import User, Appointment, Service, AppointmentStatus
from security import get_current_user

router = APIRouter(prefix="/api/appointments", tags=["appointments"])


class BookingRequest(BaseModel):
    service_id: int
    location: str
    appointment_datetime: str


@router.post("/book")
def book_appointment(
    request: BookingRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):

    service = db.query(Service).filter(Service.id == request.service_id).first()

    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    try:
        appt_datetime = datetime.fromisoformat(request.appointment_datetime)
    except ValueError:
        raise HTTPException(
            status_code=400, detail="Invalid datetime format. Use: YYYY-MM-DDTHH:MM:SS"
        )

    start = 8
    end = 17

    if appt_datetime.hour < start or appt_datetime.hour >= end:
        raise HTTPException(
            status_code=400, detail="Please select a time between 08:00 and 17:00"
        )

    conflict = (
        db.query(Appointment)
        .filter(
            Appointment.location == request.location,
            Appointment.appointment_datetime == appt_datetime,
            Appointment.status != AppointmentStatus.cancelled,
        )
        .first()
    )

    if conflict:
        raise HTTPException(status_code=409, detail="This time slot is already taken")

    new_appointment = Appointment(
        patient_id=current_user.id,
        service_id=service.id,
        location=request.location,
        appointment_datetime=appt_datetime,
        status=AppointmentStatus.pending,
    )

    db.add(new_appointment)
    db.commit()
    db.refresh(new_appointment)

    return {
        "message": "Appointment booked successfully!",
        "appointment_id": new_appointment.id,
        "patient": current_user.first_name,
        "service": service.name,
        "location": new_appointment.location,
        "datetime": new_appointment.appointment_datetime,
        "status": new_appointment.status.value,
    }


@router.get("/slots")
def get_available_slots(
    location: str, date: str, service_id: int, db: Session = Depends(get_db)
):
    try:
        selected_date = datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(
            status_code=400, detail="Invalid date format. Use: YYYY-MM-DD"
        )

    booked = (
        db.query(Appointment)
        .options(joinedload(Appointment.service))
        .filter(
            Appointment.location == location,
            Appointment.appointment_datetime >= selected_date.replace(hour=0, minute=0),
            Appointment.appointment_datetime
            <= selected_date.replace(hour=23, minute=59),
            Appointment.status != AppointmentStatus.cancelled,
        )
        .all()
    )

    booked_times = [
        {
            "start": a.appointment_datetime,
            "end": a.appointment_datetime
            + timedelta(minutes=a.service.duration_minutes),
        }
        for a in booked
    ]

    service = db.query(Service).filter(Service.id == service_id).first()

    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    duration = service.duration_minutes

    start = selected_date.replace(hour=8, minute=0)
    lunch_start = selected_date.replace(hour=12, minute=0)
    lunch_end = selected_date.replace(hour=13, minute=0)
    end = selected_date.replace(hour=17, minute=0)

    all_slots = []
    current = start

    while current < end:
        if not (lunch_start <= current < lunch_end):
            all_slots.append(current.strftime("%H:%M"))
        current = current + timedelta(minutes=30)

    def is_available(s):
        slot_dt = selected_date.replace(
            hour=int(s.split(":")[0]), minute=int(s.split(":")[1])
        )

        return not any(b["start"] <= slot_dt < b["end"] for b in booked_times)

    return {
        "location": location,
        "date": date,
        "slots": [{"time": s, "available": is_available(s)} for s in all_slots],
    }
