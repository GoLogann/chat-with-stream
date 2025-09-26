from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    PORT: int = Field(default=8000)

    AWS_PROFILE: str | None = Field(default=None)
    AWS_REGION: str = Field(default="us-east-1")
    AWS_ENDPOINT_URL: str | None = Field(default=None)

    AWS_ACCESS_KEY_ID: str | None = Field(default=None)   
    AWS_SECRET_ACCESS_KEY: str | None = Field(default=None)

    DDB_TABLE: str = Field(default="ChatAppTable")

    BEDROCK_MODEL_ID: str = Field(
        default="us.anthropic.claude-3-7-sonnet-20250219-v1:0"
    )
    TEMPERATURE: float = Field(default=0.3)

    DEFAULT_TTL_SECONDS: int = Field(default=0)

    USE_DYNAMODB_LOCAL: bool = Field(default=False)

    class Config:
        env_file = ".env"
        extra = "allow"
