from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from web3 import AsyncWeb3


class Settings(BaseSettings):
    AVAX_RPC: str  # Default
    ETH_RPC: str | None = None  # Optional

    REDIS_URL: str

    LOG_LEVEL: str = "INFO"

    CONTRACT_ADDRESS: str = "0x66357dCaCe80431aee0A7507e2E361B7e2402370"

    # CORS Security
    allowed_origins: list[str] = [
        "http://localhost:8000",
    ]

    # RPC Limitation: https://www.ankr.com/docs/rpc-service/service-plans/#block-range--batch-size-limits
    max_block_range: int = 3000

    # Redis cache TTL
    cache_ttl: int = 180

    @field_validator("CONTRACT_ADDRESS")
    @classmethod
    def validate_contract_address(cls, value: str) -> str:
        if not AsyncWeb3.is_address(value):
            raise ValueError(f"Invalid Ethereum address: {value}")
        return AsyncWeb3.to_checksum_address(value)

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
