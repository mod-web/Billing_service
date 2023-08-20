import os
from logging import config as logging_config
from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings


from logger import LOGGING

logging_config.dictConfig(LOGGING)
load_dotenv()


class Settings(BaseSettings):
    DB_HOST: str = Field('billing_postgres')
    DB_NAME: str = Field('admin_db')
    DB_USER: str = Field('user')
    DB_PASS: str = Field('pass')
    DB_PORT: str = Field('5432')
    project_name: str = Field(..., env='PROJECT_NAME')
    base_dir: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    auth_service_url: str = Field(..., env='AUTH_SERVICE_URL')

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


settings = Settings()
