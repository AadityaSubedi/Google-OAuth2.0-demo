import requests
from requests.models import Response

from fastapi import HTTPException
import config
from typing import Union, Dict, Any
from fastapi import status
from config import Settings
from functools import lru_cache

from fastapi import Depends, FastAPI
from enum import Enum


class GoogleAuth:

    # dict to map scopes to db keys(human readable)
    scopes_dict = {"https://www.googleapis.com/auth/drive.readonly": "drive_readonly",
                   "openid profile email": "login"}

    settings = Settings()

    def get_auth_url(self, scope: str):
        # print(GoogleAuth.settings.REDIRECT_URI)
        url = f"{GoogleAuth.settings.AUTH_BASE_URL}?client_id={GoogleAuth.settings.CLIENT_ID}&redirect_uri={GoogleAuth.settings.REDIRECT_URI}&response_type=code&scope={scope}&access_type=offline"
        return url

    def exchange_auth_code_for_token(self, auth_code: str, scope: str):

        payload = {"code": auth_code, "client_id": GoogleAuth.settings.CLIENT_ID,
                   "client_secret": GoogleAuth.settings.CLIENT_SECRET, "redirect_uri": GoogleAuth.settings.REDIRECT_URI, "scope": scope, "grant_type": GoogleAuth.settings.GRANT_TYPE,
                   "access_type": "offline"}

        # Counter for retries
        retries = 0
        # Maximum number of retries
        max_retries = 3

        response: Response = Response()

        # print(response.json())

        while retries < max_retries:
            try:
                # make request to get token
                response = requests.post(
                    GoogleAuth.settings.TOKEN_URL, data=payload)
                print(response.json())
                # Raise an exception if the request was unsuccessful
                response.raise_for_status()

                # If the request was successful, break out of the while loop
                break
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
                retries += 1
                if retries == max_retries:
                    # Raise an exception if the maximum number of retries is reached
                    raise HTTPException(
                        detail="Connection/Timeout error", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

        data = response.json()
        access_token = data.get("access_token")
        refresh_token = data.get("refresh_token")
        scope = data.get("scope")
        return access_token, refresh_token, scope


class HTTPMethod(Enum):
    GET = 1
    POST = 2

class GoogleService:

    settings = Settings()


    @staticmethod
    def fetch(method: HTTPMethod, endpoint: str, access_token) -> dict:

        # Counter for retries
        retries = 0
        # Maximum number of retries
        max_retries = 3

        response: Response = Response()
        if method == HTTPMethod.GET:
            while retries < max_retries:
                try:

                    # make request to perform action
                    headers = {"Authorization": f"Bearer {access_token}"}
                    response = requests.get(
                        f"{GoogleService.settings.GOOGLE_SERVICE_URL}{endpoint}", headers=headers)

                    response.raise_for_status()

                    # If the request was successful, break out of the while loop
                    break
                except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
                    retries += 1
                    if retries == max_retries:
                        # Raise an exception if the maximum number of retries is reached
                        raise HTTPException(
                            detail="Connection/Timeout error", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return response.json()

    def list_pdfs(self, access_token: str) -> list:
        # make request to list pdfs
        data = GoogleService.fetch(HTTPMethod.GET, "/drive/v3/files", access_token)

        # traverse through all the files and filter only pdfs
        pdf_files = filter(
            lambda file: file["mimeType"] == "application/pdf", data["files"])

        return list(pdf_files)

    def get_google_user_info(self, access_token: str) -> Union[dict, None]:
        # make request to list pdfs
        data = GoogleService.fetch(
            HTTPMethod.GET, "/oauth2/v1/userinfo", access_token)
        return data
