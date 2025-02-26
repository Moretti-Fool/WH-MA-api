from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from database import Base, engine
from config import settings
from routers import users, oauth

app = FastAPI()

# Create database tables
Base.metadata.create_all(bind=engine)

origins = ["*"]

app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY_GOOGLE_AUTH)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)




# Include authentication routes
app.include_router(users.router)
app.include_router(oauth.router)


@app.get("/")
def root():
    return {"message": "Welcome!"}