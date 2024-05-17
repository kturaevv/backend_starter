import pytest

from src.auth.models import UserRoles
from src.auth.schemas import AuthUser
from src.auth.service.domain import create_user_with_password_and_role
from src.utils import generate_random_password


@pytest.fixture(scope="function")
async def register_admin_user() -> AuthUser:
    """Setup a temporary test database and configure the application to use it."""
    admin_user = AuthUser(email="test@admin.we", password=generate_random_password())
    await create_user_with_password_and_role(admin_user, UserRoles.ADMIN)
    yield admin_user
