import requests
from requests.models import Response

from fastapi import HTTPException
import config
from typing import Union, Dict, Any
from fastapi import status


class Token:
    token_url = "https://oauth2.googleapis.com/token"
    auth_base_url = "https://accounts.google.com/o/oauth2/auth"
    scopes_dict = {"https://www.googleapis.com/auth/drive.readonly": "drive_readonly",
                   "openid profile email": "login"}

    def get_drive_auth_url(self):
        # get the authorization url
        url = f"{self.auth_base_url}?client_id={config.CLIENT_ID}&redirect_uri={config.REDIRECT_URI}&response_type=code&scope={' '.join(config.SCOPES)}&access_type=offline"
        return url

    def get_login_auth_url(self):

        url = f"{self.auth_base_url}?client_id={config.CLIENT_ID}&redirect_uri={config.REDIRECT_URI}&response_type=code&scope=openid%20email%20profile&access_type=offline"
        return url

    def exchange_auth_code_for_token(self, auth_code: str, scope: str):

        payload = {"code": auth_code, "client_id": config.CLIENT_ID,
                   "client_secret": config.CLIENT_SECRET, "redirect_uri": config.REDIRECT_URI, "scope": scope, "grant_type": config.GRANT_TYPE,
                   "access_type": "offline"}

        # Counter for retries
        retries = 0
        # Maximum number of retries
        max_retries = 1

        response: Response = Response()

        # print(response.json())

        while retries < max_retries:
            try:
                # make request to get token
                response = requests.post(Token.token_url, data=payload)
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


class GoogleApiOperation:
    google_api_url = "https://www.googleapis.com"

    @staticmethod
    def do(method: str, endpoint: str, access_token) -> Union[dict, None]:

        # Counter for retries
        retries = 0
        # Maximum number of retries
        max_retries = 3

        response: Response = Response()
        if method == "GET":
            while retries < max_retries:
                try:

                    # make request to perform action
                    headers = {"Authorization": f"Bearer {access_token}"}
                    response = requests.get(
                        f"{GoogleApiOperation.google_api_url}{endpoint}", headers=headers)

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
        data = GoogleApiOperation.do("GET", "/drive/v3/files", access_token)

        assert data is not None, "GoogleApiOperation.do() returns None"
        # traverse through all the files and filter only pdfs
        pdf_files = filter(
            lambda file: file["mimeType"] == "application/pdf", data["files"])

        return list(pdf_files)

    def get_google_user_info(self, access_token: str) -> Union[dict, None]:
        # make request to list pdfs
        data = GoogleApiOperation.do(
            "GET", "/oauth2/v1/userinfo", access_token)
        return data
