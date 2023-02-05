"""
main.py
"""
from fastapi import FastAPI, Response, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.encoders import jsonable_encoder
import requests

from fastapi.responses import RedirectResponse, JSONResponse


import json
import config
import components as comp
from typing import Any, Dict

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


@app.get("/login_authorization_url")
async def google_login_url():
    try:
        # get the authorization url
        url = comp.Token().get_login_auth_url()

        # return the url
        return JSONResponse(content={"url": url}, status_code=status.HTTP_200_OK)

    except Exception as e:
        raise HTTPException(detail={"message": str(
            e)}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@app.get("/drive_access_authorization_url")
async def auth_url():
    try:
        # get the authorization url
        url = comp.Token().get_drive_auth_url()

        # return the url
        return JSONResponse(content={"url": url}, status_code=status.HTTP_200_OK)

    except Exception as e:
        raise HTTPException(detail={"message": str(
            e)}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@app.get("/oauth2callback")
async def callback(code: str, scope: str):
    try:

        token = comp.Token()

        # Exchange the auth code for token
        access_token, refresh_token, scope = token.exchange_auth_code_for_token(
            code, scope)

        # save these tokens in db(we are using a dict as db)
        if "openid" in scope:
            scope_value = "login"
        else:
            scope_value = comp.Token.scopes_dict.get(scope)
        print("*"*10)
        if scope_value:
            db[scope_value] = {
                "access_token": access_token,
                "refresh_token": refresh_token}

            # Return the success message
            return JSONResponse(content={"message": "auth_to_token success"}, status_code=status.HTTP_200_OK)

    except Exception as e:
        return e
        raise HTTPException(detail=
            {"message": str(e)}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@app.get("/list_pdfs")
async def listpdfs():
    try:
        google_api_operation = comp.GoogleApiOperation()
        files = google_api_operation.list_pdfs(
            db["drive_readonly"]["access_token"])

        files = jsonable_encoder(files)

        return JSONResponse(content={"message": "pdfs retrieve success", "data": files}, status_code=status.HTTP_200_OK)

    except Exception as e:
        raise HTTPException(detail=str(
            e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@app.get("/google_profile")
async def google_profile():
    try:
        google_api_operation = comp.GoogleApiOperation()
        data = google_api_operation.get_google_user_info(
            db["login"]["access_token"])

        data = jsonable_encoder(data)

        return JSONResponse(content={"message": "user data retrieve success", "data": data}, status_code=status.HTTP_200_OK)

    except Exception as e:
        raise HTTPException(detail=str(
            e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
