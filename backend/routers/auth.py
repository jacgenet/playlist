from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import Admin
from schemas import AdminCreate, AdminLogin, Token, AdminResponse
from auth import (
    authenticate_admin, 
    create_access_token, 
    get_password_hash, 
    get_admin_by_email,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    get_current_admin
)

router = APIRouter()

@router.post("/register", response_model=AdminResponse)
async def register_admin(admin_data: AdminCreate, db: Session = Depends(get_db)):
    # Check if admin already exists
    existing_admin = get_admin_by_email(db, admin_data.email)
    if existing_admin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new admin
    hashed_password = get_password_hash(admin_data.password)
    db_admin = Admin(
        email=admin_data.email,
        hashed_password=hashed_password
    )
    db.add(db_admin)
    db.commit()
    db.refresh(db_admin)
    
    return db_admin

@router.post("/login", response_model=Token)
async def login_admin(admin_data: AdminLogin, db: Session = Depends(get_db)):
    admin = authenticate_admin(db, admin_data.email, admin_data.password)
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": admin.email}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=AdminResponse)
async def get_current_admin_info(current_admin: Admin = Depends(get_current_admin)):
    return current_admin
