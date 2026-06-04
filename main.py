from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, field_validator
from routers.auth import router as auth_router
from routers.patients import router as patients_router
from routers.appointments import router as appointments_router
from routers.services import router as services_router
from routers.locations import router as locations_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(patients_router)
app.include_router(appointments_router)
app.include_router(services_router)
app.include_router(locations_router)


class BookingRequest(BaseModel):
    patient_name: str
    email: str
    service: str
    preferred_date: str
    preferred_time: str

    @field_validator(
        "patient_name", "email", "service", "preferred_date", "preferred_time"
    )
    def must_not_be_empty(cls, value, info):
        if not value.strip():
            raise ValueError(f"{info.field_name} cannot be empty")
        return value


@app.get("/")
def home():
    return {"message": "Dental Booking API is running"}


@app.post("/api/book")
def book_appointment(booking: BookingRequest):
    return {
        "message": f"Booking received for {booking.patient_name}!",
        "service": booking.service,
        "date": booking.preferred_date,
        "time": booking.preferred_time,
    }
