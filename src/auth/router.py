import fastapi_sso
from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    HTTPException,
    Request,
    Response,
    status,
)
from fastapi.responses import RedirectResponse

from src.auth import service
from src.auth.config import google_sso
from src.auth.dependencies import (
    email_not_taken,
    valid_admin_user,
    valid_authenticated_user,
    valid_refresh_token,
    valid_refresh_token_user,
)
from src.auth.models import AuthRefreshTokenModel, AuthUserModel
from src.auth.schemas import (
    AccessTokenResponse,
    AuthUser,
    BaseUser,
    JWTData,
)
from src.exceptions import BadRequest, DetailedHTTPException

router = APIRouter(prefix="/auth")


@router.get("/me", response_model=BaseUser)
async def get_my_account(
    jwt_data: JWTData = Depends(valid_authenticated_user),
) -> BaseUser:
    user = await service.get_user_by_id(jwt_data.user_id)
    if not user:
        raise DetailedHTTPException
    return BaseUser(**user.data)


@router.get("/admin", include_in_schema=False)
async def test_admin_access_endpoint(
    _: JWTData = Depends(valid_admin_user),
) -> str:
    return "ok"


@router.post("/signup", status_code=status.HTTP_201_CREATED, response_model=BaseUser)
async def register_user(
    auth_data: AuthUser = Depends(email_not_taken),
) -> BaseUser | HTTPException:
    user = await service.create_user_with_password(auth_data)
    if not user:
        raise DetailedHTTPException
    return user


@router.post("/signin", response_model=AccessTokenResponse)
async def auth_user(
    response: Response, user: AuthUserModel = Depends(service.authenticate_user)
) -> AccessTokenResponse:
    access_token_value = service.jwts.create_access_token(user=user)
    refresh_token_value = await service.create_refresh_token(user_id=user.id)

    response.set_cookie(
        **service.token.get_refresh_token_settings(refresh_token_value).data
    )
    response.set_cookie(
        **service.token.get_access_token_settings(access_token_value).data
    )

    return AccessTokenResponse(
        access_token=access_token_value,
        refresh_token=refresh_token_value,
    )


@router.put("/token", response_model=AccessTokenResponse)
async def refresh_token(
    worker: BackgroundTasks,
    response: Response,
    refresh_token: AuthRefreshTokenModel = Depends(valid_refresh_token),
    user: AuthUserModel = Depends(valid_refresh_token_user),
) -> AccessTokenResponse:
    access_token_value = service.jwts.create_access_token(user=user)
    refresh_token_value = await service.create_refresh_token(user_id=user.id)

    response.set_cookie(
        **service.token.get_refresh_token_settings(refresh_token_value).data
    )
    response.set_cookie(
        **service.token.get_access_token_settings(access_token_value).data
    )

    worker.add_task(service.expire_refresh_token, refresh_token.uuid)

    return AccessTokenResponse(
        access_token=access_token_value,
        refresh_token=refresh_token_value,
    )


@router.delete("/token")
async def logout_user(
    response: Response,
    refresh_token: AuthRefreshTokenModel = Depends(valid_refresh_token),
) -> None:
    await service.expire_refresh_token(refresh_token.uuid)

    response.delete_cookie("accessToken")
    response.delete_cookie(
        **service.token.get_refresh_token_settings(
            refresh_token.refresh_token, expired=True
        ).model_dump(exclude_unset=True, exclude_defaults=True)
    )


# Google SSO login


@router.get("/google/login")
async def google_login() -> RedirectResponse:
    with google_sso:
        return await google_sso.get_login_redirect(
            params={"prompt": "consent", "access_type": "offline"}
        )


@router.get("/google/callback")
async def google_callback(request: Request) -> RedirectResponse:
    """Process login response from Google and return user info"""

    with google_sso:
        user: fastapi_sso.OpenID | None = await google_sso.verify_and_process(request)

    if user is None or user.email is None:
        raise BadRequest

    user_stored = await service.get_user_by_email(user.email)
    if not user_stored:
        user_stored = await service.create_user_with_sso(user.email)
        assert user_stored is not None, "Empty user returned"

    access_token_value = service.jwts.create_access_token(user=user_stored)
    refresh_token_value = await service.create_refresh_token(user_id=user_stored.id)

    response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    response.set_cookie(
        **service.token.get_refresh_token_settings(refresh_token_value).data
    )
    response.set_cookie(
        **service.token.get_access_token_settings(access_token_value).data
    )
    return response
