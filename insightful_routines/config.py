from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    api_token: SecretStr = Field(default=None)
    postgres_uri: str = Field(default=None)
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
