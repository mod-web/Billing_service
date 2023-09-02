from pydantic_settings import BaseSettings
from pydantic import Field


class Billing(BaseSettings):
    host: str = Field('localhost')
    port: int = Field(8001)


class BaseConfig(BaseSettings):
    billing: Billing = Billing()

    class Config:
        env_file = '.env'
        env_nested_delimiter = "__"
        env_file_encoding = 'utf-8'


cfg = BaseConfig()
