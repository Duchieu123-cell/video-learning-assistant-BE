from fastapi import APIRouter, status
from app.core.security import hash_password
from app.models.user import User
from app.schemas.user import RegisterRequest
from app.core.dependencies import DBSession
from app.core.exceptions import BadRequestException
from sqlalchemy import select

router = APIRouter(
    prefix="/users",
    tags=["User"]
)

@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
)
async def register_user(user: RegisterRequest, db: DBSession):
    # Kiểm tra trùng email
    stmt = (
        select(User)
        .where(User.email == user.email)
    )
    existing_email = (await db.execute(stmt)).scalar_one_or_none()
    if existing_email:
        raise BadRequestException("Email đã tồn tại. Vui lòng sử dụng email khác.")

    # Hash the password
    hashed_password = hash_password(user.password)

    # Create a new user
    new_user = User(
        email=user.email,
        hashed_password=hashed_password,
        full_name=user.full_name
    )
    
    db.add(new_user)
    await db.flush()
    await db.refresh(new_user)

    return {
        "user_id": new_user.id
    }
