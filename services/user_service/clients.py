import os

import httpx


class BillingClient:
    def __init__(self, base_url: str | None = None):
        self.base_url = base_url or os.getenv("BILLING_SERVICE_URL", "http://localhost:8001")
        self._client = httpx.AsyncClient(base_url=self.base_url)

    async def create_account(self, user_id: int) -> None:
        await self._client.post("/accounts", json={"user_id": user_id})

    async def close(self):
        await self._client.aclose()
