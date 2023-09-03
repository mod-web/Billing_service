from pydantic_settings import BaseSettings
from pydantic import Field


class Billing(BaseSettings):
    host: str = Field('localhost')
    port: int = Field(8001)


class Yoo_kassa(BaseSettings):
    account_id: int = Field(123)
    secret_key: str = Field('secret')


class BaseConfig(BaseSettings):
    billing: Billing = Billing()
    yookassa: Yoo_kassa = Yoo_kassa()

    class Config:
        env_file = '.env'
        env_nested_delimiter = "__"
        env_file_encoding = 'utf-8'


cfg = BaseConfig()
