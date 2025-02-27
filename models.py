from sqlalchemy import Integer, Column, String, Boolean, DateTime
from datetime import datetime, timedelta
from database import Base


class User(Base):
    __tablename__ = "users"

    email = Column(String, primary_key=True, index=True)
    password_hash = Column(String, nullable=False)
    is_verified = Column(Boolean, default=False)
    verification_token = Column(String, unique=True, nullable=True)
    token_expires_at = Column(DateTime, nullable=True)
    auth_provider = Column(String, nullable=False)
