from pydantic_settings import BaseSettings

# this is to validate our environment variables -> this schema will fetch and validate our environment variable from our system
class Settings(BaseSettings): # CASE INSENSITIVE BUT BEST PRACTICE IS TO SET THEM CAPITALIZE
    DATABASE_HOSTNAME: str
    DATABASE_PORT: str
    DATABASE_PASSWORD: str
    DATABASE_NAME: str
    DATABASE_USERNAME: str
    SECRET_KEY: str 
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    SMTP_SERVER: str
    SMTP_PORT: int
    SMTP_EMAIL: str
    SMTP_PASSWORD: str
    VERIFICATION_TOKEN_EXPIRE: int
    
    class Config:
        env_file = ".env"

settings =  Settings()