import secrets
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from database import get_db
from models import User
from schemas import UserCreate, UserResponse
from config import settings
from utils.security import get_current_user, hash_password, verify_password, create_access_token
from utils.email import send_email

router = APIRouter(
    prefix="/users",
    tags=["Authentication"]
)
@router.post("/register")
def register(user: UserCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = hash_password(user.password)
    verification_token = secrets.token_urlsafe(32)  # Generate unique token

    new_user = User(
        email=user.email,
        password_hash=hashed_password,
        verification_token=verification_token,
        is_verified=False,
        token_expires_at=datetime.utcnow() + timedelta(minutes=settings.VERIFICATION_TOKEN_EXPIRE),  # Set expiry
        auth_provider="Local"
    )
    db.add(new_user)
    db.commit()

    # Send verification email
    verification_link = f"http://127.0.0.1:8000/users/verify-email?token={verification_token}"
    email_body = f"""
    <html>
        <body>
            <h3>Welcome to Our App!</h3>
            <p>Click the link below to verify your email:</p>
            <a href="{verification_link}">Verify Email</a>
        </body>
    </html>
    """
    background_tasks.add_task(send_email, user.email, "Verify Your Email", email_body)

    return {"message": "User registered. Check your email to verify your account."}



@router.get("/verify-email")
def verify_email(token: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.verification_token == token)
    user_query = user.first()
    
    if not user_query:
        raise HTTPException(status_code=400, detail="Invalid token")
    
    if user_query.token_expires_at and datetime.utcnow() > user_query.token_expires_at:
        db.delete(user_query)
        db.commit()
        raise HTTPException(status_code=400, detail="Token expired")

    
    user_query.is_verified = True
    user_query.verification_token = None  # Invalidate token
    user_query.token_expires_at = None
    db.commit()
    
    return {"message": "Email verified successfully"}

@router.post("/login")
def login(email: str, password: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    #  If the user is an OAuth user , enforce Google login
    if user.auth_provider=="Google":
        raise HTTPException(status_code=400, detail="Use Google OAuth to log in")

    #  Check email verification **before** password verification
    if not user.is_verified:
        raise HTTPException(status_code=403, detail="Email not verified. Please check your email.")

    #  Verify password
    if not verify_password(password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    #  Generate access token
    access_token = create_access_token(data={"sub": user.email})
    response = JSONResponse(content={"message": "Login successful"})
    response.set_cookie(key="access_token", value=access_token, httponly=True, samesite="Lax", secure=True)
    return response

@router.post("/logout")
def logout():
    response = JSONResponse(content={"message": "Logged out successfully"})
    response.delete_cookie("access_token")  # Remove the access token
    return response



@router.get("/me")
def get_user_details(current_user: User = Depends(get_current_user)):
    return {"email": current_user.email, "is_verified": current_user.is_verified}





