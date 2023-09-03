from pydantic_settings import BaseSettings
from pydantic import Field


class Broker(BaseSettings):
    host: str = Field("localhost")
    port: int = Field(2128)
    login: str = Field("login")
    password: str = Field("password")
    instant_queue: str = Field("queue1")
    delayed_queue: str = Field("queue2")


class Elastic(BaseSettings):
    key: str = Field("token")
    email_from: str = Field("email")


class BaseConfig(BaseSettings):
    broker: Broker = Broker()
    elastic: Elastic = Elastic()

    class Config:
        env_file = "./.env"
        env_nested_delimiter = "__"


cfg = BaseConfig()
