from fastapi import FastAPI
from database import Base, engine
from auth.users import router as auth_router

app = FastAPI()

# Create database tables
Base.metadata.create_all(bind=engine)

# Include authentication routes
app.include_router(auth_router, prefix="/auth")
