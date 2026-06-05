from database import SessionLocal
from models import Service

db = SessionLocal()

services = [
    Service(name="Returning Patient Hygiene", duration_minutes=60),
    Service(name="Emergency Dental Exam", duration_minutes=30),
    Service(name="New Patient Exam & X-Rays", duration_minutes=90),
    Service(name="Whitening Consultation", duration_minutes=45),
]

for service in services:
    db.add(service)

db.commit()
print("Seeded successfully!")
db.close()
