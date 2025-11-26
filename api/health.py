from typing import Any


async def health_check() -> dict[str, Any]:
    return {"status": "healthy"}
