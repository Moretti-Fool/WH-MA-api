from datetime import timedelta
import logging
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from starlette.requests import Request
from starlette.responses import RedirectResponse
from authlib.integrations.starlette_client import OAuth, OAuthError
from sqlalchemy.orm import Session
from config import settings
from database import get_db
from utils.security import generate_placeholder_password, create_access_token
from models import User

router = APIRouter(
    prefix="/google",
    tags=["Google OAUTH"]
)


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
oauth = OAuth()

oauth.register(
    name="google",
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration", #This is a standard URL that provides Google's OAuth configuration details, such as token endpoints
    redirect_uri=settings.GOOGLE_REDIRECT_URI,
    client_kwargs={
        'scope': 'openid email profile', # Specifies what data we want from the user (their email, profile info, etc.).
        'prompt': 'select_account', #Ensures that users can pick a Google account each time they log in.
    }
)




# Step 1: Redirect to Google's OAuth Page
@router.get("/login")
async def login(request: Request):
    next_url = request.query_params.get("next", "/") #If the user was trying to access a page before logging in, we store it so they can be redirected back after authentication.
    request.session["next_url"] = next_url #This allows the application to remember where the user wanted to go before logging in.
    return await oauth.google.authorize_redirect(request, settings.GOOGLE_REDIRECT_URI) #redirects the user to Google's OAuth page.

#Step 2: Handle Google's OAuth Callback
'''The callback happens after the user logs in using Google. Google sends an authorization code to our backend, '
'which we then exchange for an access token. This access token is used to get the user's profile details. '''
@router.get("/callback")
async def auth(request: Request, db: Session = Depends(get_db)):
    # when google redirect to this route after login, it send a auth code with it
    # backend receives it
    # send it to google to ger an access token
    try:
        token = await oauth.google.authorize_access_token(request) # store that token here
        user = token.get('userinfo') # get user info from access token and store it in a variable
        if not user:
            raise HTTPException(status_code=400, detail="Failed to retrieve user info")


        email = user.get('email')
        db_user = db.query(User).filter(User.email == email).first()
        if not db_user:
            # Create new user if not exists
            new_user = User(
                email=email,
                password_hash=generate_placeholder_password(),  
                is_verified=True,  # Google users are already verified
                verification_token=None,
                token_expires_at=None,
                auth_provider="Google"
            )
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            db_user = new_user

        access_token = create_access_token(data={"sub": email})

        # Store tokens in HTTP-only cookies
        response = JSONResponse(content={"message": "Login successful"})
        response.set_cookie(key="access_token", value=access_token, httponly=True, samesite="Lax", secure=True)
        return response

    except OAuthError as error:
        logger.error(f"OAuth Error: {error}")
        raise HTTPException(status_code=400, detail="Authentication failed")

@router.get("/logout")
async def logout(request: Request):
    request.session.pop("user", None)  # Remove user session
    request.session.clear()
    return RedirectResponse(url="/")
