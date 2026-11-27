from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status

from app.core.deps import CurrentUser, get_auth_service
from app.schemas.auth import LoginRequest, RefreshRequest, RegisterRequest, TokenPair
from app.schemas.user import UserRead
from app.services.auth import AuthError, AuthService, UserAlreadyExistsError

router = APIRouter(prefix="/auth", tags=["auth"])

Service = Annotated[AuthService, Depends(get_auth_service)]


def _unauthorized(exc: AuthError) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=str(exc),
        headers={"WWW-Authenticate": "Bearer"},
    )


@router.post(
    "/register",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    responses={409: {"description": "Email or username already registered"}},
)
async def register(body: RegisterRequest, service: Service):
    try:
        return await service.register(body.email, body.username, body.password)
    except UserAlreadyExistsError as exc:
        raise HTTPException(status.HTTP_409_CONFLICT, str(exc)) from None


@router.post("/login", response_model=TokenPair, responses={401: {"description": "Wrong credentials"}})
async def login(body: LoginRequest, service: Service):
    try:
        return await service.login(body.email, body.password)
    except AuthError as exc:
        raise _unauthorized(exc) from None


@router.post(
    "/refresh",
    response_model=TokenPair,
    responses={401: {"description": "Refresh token invalid, expired, revoked or already used"}},
)
async def refresh(body: RefreshRequest, service: Service):
    """Exchange a refresh token for a new pair. The old refresh token stops working."""
    try:
        return await service.refresh(body.refresh_token)
    except AuthError as exc:
        raise _unauthorized(exc) from None


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={401: {"description": "Refresh token invalid or expired"}},
)
async def logout(body: RefreshRequest, service: Service):
    """Revoke the refresh token. Access tokens expire on their own (short lifetime)."""
    try:
        await service.logout(body.refresh_token)
    except AuthError as exc:
        raise _unauthorized(exc) from None
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/me", response_model=UserRead, responses={401: {"description": "Not authenticated"}})
async def me(user: CurrentUser):
    """Protected route example: requires `Authorization: Bearer <access token>`."""
    return user
