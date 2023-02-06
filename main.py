"""
main.py
"""
from fastapi import FastAPI, Response, HTTPException, Request, status, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.encoders import jsonable_encoder
import requests

from fastapi.responses import RedirectResponse, JSONResponse


import components as comp
from typing import Any, Dict


router = APIRouter(
    prefix="/google/auth",
    tags=["google", "auth"],

)

app = FastAPI()


db: Dict[str, Any] = {"drive": {}, "login": {}}  # store the tokens


origins = [
    "http://localhost:3000",
    "http://localhost:8000",
    "http://localhost"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from typing import Union
@router.get("/authorize")
async def google_login_url(scope:str):
    try:
        scope_ = "" # scope to be passed to google auth url:

        if "profile" in scope:
            scope_ = "openid%20profile%20email"

        elif scope == "drive_readonly":
            scope_ = "https://www.googleapis.com/auth/drive.readonly"

        # get the authorization url
        url = comp.GoogleAuth().get_auth_url(scope_)

        # return the url
        return JSONResponse(content={"url": url}, status_code=status.HTTP_200_OK)

    except Exception as e:
        raise HTTPException(detail={"message": str(
            e)}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.get("/oauth2callback")
async def callback(code: str, scope: str):
    try:

        token = comp.GoogleAuth()

        # Exchange the auth code for token
        access_token, refresh_token, scope = token.exchange_auth_code_for_token(
            code, scope)

        data = {}
        # save these tokens in db(we are using a dict as db)
        if "openid" in scope:
            scope_value = "login"
        else:
            scope_value = comp.GoogleAuth.scopes_dict.get(scope)
        if scope_value:
            db[scope_value] = {
                "access_token": access_token,
                "refresh_token": refresh_token}
            
            
        # retrieve the user info
        if db["login"].get("access_token"):    
            google_api_operation = comp.GoogleService()
            data = google_api_operation.get_google_user_info(
                db["login"]["access_token"])

        data = jsonable_encoder(data)

        # Return the success message
        return JSONResponse(content={"message": "auth_to_token success", "data": data}, status_code=status.HTTP_200_OK)

    except Exception as e:
        raise HTTPException(detail={"message": str(
            e)}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.get("/drive/pdfs")
async def listpdfs():
    try:
        google_api_operation = comp.GoogleService()
        files = google_api_operation.list_pdfs(
            db["drive_readonly"]["access_token"])

        files = jsonable_encoder(files)

        return JSONResponse(content={"message": "pdfs retrieve success", "data": files}, status_code=status.HTTP_200_OK)

    except Exception as e:
        raise HTTPException(detail=str(
            e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


# include the router
app.include_router(router)
