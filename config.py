

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
