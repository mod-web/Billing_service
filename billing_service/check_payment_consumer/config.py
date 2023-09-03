from pydantic_settings import BaseSettings
from pydantic import Field


class Kafka(BaseSettings):
    host: str = Field('localhost')
    port: int = Field(29092)


class Yoo_kassa(BaseSettings):
    account_id: int = Field(123)
    secret_key: str = Field('secret')


class BaseConfig(BaseSettings):
    kafka: Kafka = Kafka()
    yookassa: Yoo_kassa = Yoo_kassa()

    class Config:
        env_file = '.env'
        env_nested_delimiter = "__"
        env_file_encoding = 'utf-8'


cfg = BaseConfig()
