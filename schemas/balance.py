from pydantic import BaseModel, Field, field_validator
from web3 import AsyncWeb3


class BalanceRequest(BaseModel):
    block_number: int = Field(..., ge=0)
    address: str
    chain_id: int | None = Field(default=43114)  # Default Avalanche

    @field_validator("address")
    @classmethod
    def check_checksum(cls, value: str) -> str:
        if not AsyncWeb3.is_address(value):
            raise ValueError("Invalid Ethereum address")
        return AsyncWeb3.to_checksum_address(value)


class BalanceResponse(BaseModel):
    address: str = Field(..., description="Address from request")
    balance: int = Field(..., description="Native balance in WEI")
