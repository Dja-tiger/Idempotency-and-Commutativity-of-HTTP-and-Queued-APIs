import os

import httpx


class BillingClient:
    def __init__(self, base_url: str | None = None):
        self.base_url = base_url or os.getenv("BILLING_SERVICE_URL", "http://localhost:8001")
        self._client = httpx.AsyncClient(base_url=self.base_url)

    async def withdraw(self, user_id: int, amount: float) -> dict:
        response = await self._client.post(f"/accounts/{user_id}/withdraw", json={"amount": amount})
        response.raise_for_status()
        return response.json()

    async def close(self):
        await self._client.aclose()


class NotificationClient:
    def __init__(self, base_url: str | None = None):
        self.base_url = base_url or os.getenv("NOTIFICATION_SERVICE_URL", "http://localhost:8002")
        self._client = httpx.AsyncClient(base_url=self.base_url)

    async def send_email(self, user_id: int, email: str, subject: str, body: str) -> None:
        await self._client.post(
            "/notifications",
            json={"user_id": user_id, "email": email, "subject": subject, "body": body},
        )

    async def close(self):
        await self._client.aclose()


class UserClient:
    def __init__(self, base_url: str | None = None):
        self.base_url = base_url or os.getenv("USER_SERVICE_URL", "http://localhost:8000")
        self._client = httpx.AsyncClient(base_url=self.base_url)

    async def get_user(self, user_id: int) -> dict:
        response = await self._client.get(f"/users/{user_id}")
        response.raise_for_status()
        return response.json()

    async def close(self):
        await self._client.aclose()
