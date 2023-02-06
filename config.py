API_KEY = "b3d9b7d79a7047d1a99392c68c95d4f7"
CLIENT_ID="1020532829824-8cir171h9s0426f122etjm7ai2795dsm.apps.googleusercontent.com"
CLIENT_SECRET="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"
GRANT_TYPE="authorization_code"
REDIRECT_URI="http://localhost:8000/oauth2callback"
SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]
ACCESS_TOKEN = "ya29.a0AVvZVsqGbd84ZGiw3s1NirSLuuWdPUbGRNlTayiJNkIuTY4goFLCNhh4-1pnczcxd799uLYc31qsot5B2XB_zuzIUhenFENFxOrjXTkDKxUsxDuCbwLTXnxNSwSwzYbCYPK2by7sD7xx811J2PqfV2gp65bBaCgYKAYsSARESFQGbdwaIg8YPVQMFoxliwrnunWhOMQ0163"


from pydantic import BaseSettings


class Settings(BaseSettings):
    API_KEY: str  = ""
    CLIENT_ID: str =""
    CLIENT_SECRET: str =""
    GRANT_TYPE:str=""
    REDIRECT_URI:str=""
    TOKEN_URL:str=""
    AUTH_BASE_URL:str=""
    GOOGLE_SERVICE_URL: str ="" 
    
    
    class Config:
        env_file = ".env_var"