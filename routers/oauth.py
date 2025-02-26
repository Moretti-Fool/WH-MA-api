from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse
from starlette.requests import Request
import logging
from starlette.responses import RedirectResponse
from authlib.integrations.starlette_client import OAuth, OAuthError
from config import settings

router = APIRouter(
    prefix="/auth",
    tags=["OAUTH Authentication"]
)


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
oauth = OAuth()

oauth.register(
    name="google",
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    redirect_uri=settings.GOOGLE_REDIRECT_URI,
    client_kwargs={
        'scope': 'openid email profile',
        'prompt': 'select_account',
    }
)




# Step 1: Redirect to Google's OAuth Page
@router.get("/login")
async def login(request: Request):
    next_url = request.query_params.get("next", "/")
    request.session["next_url"] = next_url
    return await oauth.google.authorize_redirect(request, settings.GOOGLE_REDIRECT_URI)

#Step 2: Handle Google's OAuth Callback
@router.get("/callback")
async def auth(request: Request):
    try:
        token = await oauth.google.authorize_access_token(request)
        user = token.get('userinfo')
        if user:
            request.session['user'] = dict(user)
            return RedirectResponse(url='/')
    except OAuthError as error:
        logger.error(f"OAuth Error: {error}")
        raise HTTPException(status_code=400, detail="Authentication failed")

@router.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/")

# @router.get("/callback")
# async def auth_callback(request: Request):
#     try:
#         token = await oauth.google.authorize_access_token(request)
#         user_info = await oauth.google.parse_id_token(request, token)
        
#         # Process user info (store in DB, create session, etc.)
#         return {"message": "Login successful", "user": user_info}
    
#     except Exception as e:
#         raise HTTPException(status_code=400, detail="OAuth authentication failed")




# @router.get("/callback")
# async def auth_callback(request: Request):
#     try:
#         token = await oauth.google.authorize_access_token(request)
#         print("Token Response:", token)  # Log full token response

#         id_token = token.get("id_token")
#         if id_token:
#             print("ID Token:", id_token)

#         user_info = await oauth.google.parse_id_token(request, token)
#         print("User Info:", user_info)  # Print user details

#         return {"message": "Login successful", "user": user_info}

    # except Exception as e:
    #     print("OAuth error:", str(e))  # Log the error
    #     raise HTTPException(status_code=400, detail=f"OAuth authentication failed: {str(e)}")






# @router.get("/callback")
# async def auth_callback(request: Request):
#     print(await request.body())  # Print request data
#     print(request.query_params)  # Print query params
#     return {"message": "Debugging Google Callback"}


# @router.get("/callback")
# async def auth_callback(request: Request):
#     try:
#         # Exchange auth code for access token
#         token = await oauth.google.authorize_access_token(request)

#         # Fetch user info
#         user = await oauth.google.parse_id_token(request, token)

#         return {"user": user}  # ✅ Success! Returns Google profile info.
    
#     except Exception as e:
#         return {"error": str(e)}  # ❌ Debugging errors if any.




# @router.get("/callback")
# async def auth_callback(request: Request):
#     try:
#         # Debugging: Print request query parameters
#         print("Request Query Params:", request.query_params)

#         # Attempt to get access token
#         token = await oauth.google.authorize_access_token(request)
#         print("OAuth Token:", token)

#         # Attempt to get user info
#         user_info = await oauth.google.parse_id_token(request, token)
#         print("User Info:", user_info)

#         return {"message": "Login successful", "user": user_info}

#     except Exception as e:
#         print("OAuth Error:", str(e))
#         raise HTTPException(status_code=400, detail=f"OAuth authentication failed: {str(e)}")
