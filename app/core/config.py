from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    PORT: int = Field(default=8000)

    AWS_PROFILE: str | None = Field(default=None)  
    AWS_REGION: str = Field(default="us-east-1")
    BEDROCK_MODEL_ID: str = Field(default="us.anthropic.claude-3-7-sonnet-20250219-v1:0")
    TEMPERATURE: float = Field(default=0.3)

    class Config:
        env_file = ".env"
        extra = "allow"
