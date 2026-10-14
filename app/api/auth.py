from fastapi import APIRouter, Depends, Response, Cookie, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.core.dependencies import DBSession
from typing import Annotated
from app.services.auth import AuthService
from app.schemas import auth

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

@router.post(
    "/token",
    response_model=auth.LoginResponse,
    summary="Đăng nhập và lấy access token"
)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    response: Response,
    db: DBSession
):
    return await AuthService.login_user(response, form_data.username, form_data.password, db)

@router.post(
    "/refresh",
    response_model=auth.Token,
    summary="Làm mới access token"
)
async def refresh_access_token(
    response: Response,
    db: DBSession,
    refresh_token: Annotated[str | None, Cookie()] = None,

):
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Không tìm thấy Refresh Token",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    return await AuthService.refresh_access_token(response, refresh_token, db)

@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Đăng xuất và thu hồi refresh token"
)
async def logout_user(
    response: Response,
    db: DBSession,
    refresh_token: Annotated[str | None, Cookie()] = None,
):
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Không tìm thấy Refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    return await AuthService.logout_user(response, refresh_token, db)
