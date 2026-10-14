from app.core.database import get_db
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
from fastapi import HTTPException, status
from app.core.config import settings
import uuid
from app.models.user import User

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM

DBSession = Annotated[AsyncSession, Depends(get_db)]
Token = Annotated[str, Depends(OAuth2PasswordBearer(tokenUrl="/auth/token"))]

async def get_current_user(token: Token, db: DBSession) -> User:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id_str: str = payload.get("sub")
        
        if user_id_str is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail={
                    "message": "Không thể lấy user id từ accesstoken",
                    "type": "invalid_access_token"
                }
            )
            
        user_id = uuid.UUID(user_id_str)
        
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail={
                "message": "Access token đã hết hạn",
                "type": "expired_access_token"
            }
        )
    except (InvalidTokenError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail={
                "message": "Access token không hợp lệ",
                "type": "invalid_access_token"
            }
        )
        
    user = await db.get(User, user_id)
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail={
                "message": "Không tìm thấy user",
                "type": "user_not_found"
            }
        )

    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
