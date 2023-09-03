import os
from logging import config as logging_config
from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings
from logger import LOGGING


logging_config.dictConfig(LOGGING)
load_dotenv()


class Kafka(BaseSettings):
    host: str = Field('localhost')
    port: int = Field(29092)


class Yoo_kassa(BaseSettings):
    account_id: int = Field(123)
    secret_key: str = Field('secret')


class DataBase(BaseSettings):
    host: str = Field('localhost')
    name: str = Field('name')
    user: str = Field('user')
    password: str = Field('pass')
    port: str = Field('5432')


class Billing(BaseSettings):
    host: str = Field('billing_api')
    port: int = Field(8001)


class Redis(BaseSettings):
    host: str = Field('redis')
    port: int = Field(6379)


class Settings(BaseSettings):
    kafka: Kafka = Kafka()
    yookassa: Yoo_kassa = Yoo_kassa()
    db: DataBase = DataBase()
    billing: Billing = Billing()
    redis: Redis = Redis()
    project_name: str = Field('PROJECT_NAME')
    base_dir: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    auth_service_url: str = Field('AUTH_SERVICE_URL')

    class Config:
        env_file = '.env'
        env_nested_delimiter = "__"
        env_file_encoding = 'utf-8'


settings = Settings()
