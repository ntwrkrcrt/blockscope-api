from typing import Any, Sequence

from hexbytes import HexBytes
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class LogRequest(BaseModel):
    from_block: int = Field(..., ge=0)
    to_block: int | None = Field(None, ge=0)

    @model_validator(mode="after")
    def validate_block_range(self) -> "LogRequest":
        if self.to_block is not None and self.to_block < self.from_block:
            raise ValueError(
                f"to_block ({self.to_block}) must be greater than or equal to from_block ({self.from_block})"
            )
        return self


class LogReceipt(BaseModel):
    address: str
    block_hash: str = Field(alias="blockHash")
    block_number: int = Field(alias="blockNumber")
    data: str
    log_index: int = Field(alias="logIndex")
    removed: bool
    topics: Sequence[str]
    transaction_hash: str = Field(alias="transactionHash")
    transaction_index: int = Field(alias="transactionIndex")

    @field_validator("block_hash", "data", "transaction_hash", mode="before")
    @classmethod
    def convert_hexbytes(cls, value: Any) -> str:
        if isinstance(value, HexBytes):
            return value.hex()
        return value

    @field_validator("topics", mode="before")
    @classmethod
    def convert_topics(cls, value: Sequence[Any]) -> list[str]:
        return [
            topic.hex() if isinstance(topic, HexBytes) else topic for topic in value
        ]

    model_config = ConfigDict(populate_by_name=True)


class LogResponse(BaseModel):
    logs: list[LogReceipt]
