import os
from logging import config as logging_config
from dotenv import load_dotenv
from pydantic import BaseSettings, Field

from logger import LOGGING

logging_config.dictConfig(LOGGING)
load_dotenv()


class BrokerSettings(BaseSettings):
    host: str = Field(..., env='BROKER__HOST')
    port: int = Field(..., env='BROKER__PORT')
    login: str = Field(..., env='BROKER__LOGIN')
    password: str = Field(..., env='BROKER__PASSWORD')
    instant_queue: str = Field(..., env='BROKER_INSTANT_QUEUE')
    delayed_queue: str = Field(..., env='BROKER_DELAYED_QUEUE')


class Settings(BaseSettings):
    project_name: str = Field(..., env='PROJECT_NAME')
    base_dir: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    broker = BrokerSettings()
    auth_service_url: str = Field(..., env='AUTH_SERVICE_URL')

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


settings = Settings()
