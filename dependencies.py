from fastapi.security import OAuth2PasswordBearer
from sql_online_shop.database import SessionLocal
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from pydantic import ValidationError
from jose import jwt
from datetime import datetime
from sql_online_shop.schemas import UserRead, TokenPayload
from sql_online_shop import crud
import security
import config


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


reusable_oauth = OAuth2PasswordBearer(
    tokenUrl="/login",
    scheme_name="JWT"
)


def get_current_user(db: Session = Depends(get_db), token: str = Depends(reusable_oauth)) -> UserRead:
    try:
        payload = jwt.decode(token, config.JWT_SECRET_KEY, algorithms=[security.ALGORITHM], options={'verify_exp': False})
        token_data = TokenPayload(**payload)

        if datetime.fromtimestamp(token_data.exp) < datetime.now():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired",
                headers={"WWW-Authenticate": "Bearer"},
            )

    except (jwt.JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    db_user = crud.get_user_by_username(db, username=token_data.sub)

    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Could not find user",
        )

    return db_user


def is_superuser(user: UserRead = Depends(get_current_user)):
    if user.__dict__['is_superuser']:
        return user
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No permissions",
        )
