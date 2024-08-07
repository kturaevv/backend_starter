from src.auth.exceptions import DomainError
from tests.base import TestClient, pytest, status


@pytest.mark.asyncio
async def test_chat_availability_not_registered_domain(client: TestClient) -> None:
    resp = await client.get("/chat/ws")
    assert resp.status_code == DomainError.DETAIL, resp.content
    assert resp.json()["detail"] == DomainError.DETAIL, resp.content


@pytest.mark.asyncio
async def test_chat_availability_registered_domain(client: TestClient) -> None:
    resp = await client.get("/chat/ws")
    assert resp.status_code == status.HTTP_200_OK, resp.content
