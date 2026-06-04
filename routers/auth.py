from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import get_db
from models import User, UserRole
from security import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/api/auth", tags=["auth"])


class RegisterRequest(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone: str
    password: str


class LoginRequest(BaseModel):
    email: str
    password: str


@router.post("/register")
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == request.email).first()

    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = User(
        first_name=request.first_name,
        last_name=request.last_name,
        email=request.email,
        phone=request.phone,
        password_hash=hash_password(request.password),
        role=UserRole.patient,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    token = create_access_token(
        data={
            "sub": new_user.email,
            "role": new_user.role.value,
            "user_id": new_user.id,
        }
    )

    return {
        "message": f"Welcome {new_user.first_name}!",
        "access_token": token,
        "user_id": new_user.id,
        "email": new_user.email,
    }


@router.post("/login")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()

    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token(
        data={"sub": user.email, "role": user.role.value, "user_id": user.id}
    )

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "fist_name": user.first_name,
            "email": user.email,
            "role": user.role.value,
        },
    }
