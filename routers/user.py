from pydantic import ValidationError
from sql_online_shop import crud, schemas
from dependencies import get_db, is_superuser, get_current_user
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import exc
from fastapi import Depends, HTTPException, status, Body
from fastapi.routing import APIRouter
from sqlalchemy.orm import Session
import utils
import security
import config
from jose import jwt
from datetime import datetime


router = APIRouter(
    prefix="/api/v1/users",
    tags=["users"],
)


@router.post("/signup", response_model=schemas.UserRead)
def create_new_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_username = crud.get_user_by_username(db, username=user.username)
    db_email = crud.get_user_by_email(db, email=user.email)
    if db_username:
        raise HTTPException(status_code=400, detail="Username already registered")
    elif db_email:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)


@router.post('/login', response_model=schemas.TokensResponseSchema)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.get_user_by_username(db, username=form_data.username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect username or password"
        )

    user_data = user.__dict__
    if not utils.verify_password(form_data.password, user_data['hashed_password']):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect username or password"
        )

    return {
        "access_token": security.create_access_token(user_data['username']),
        "refresh_token": security.create_refresh_token(user_data['username']),
    }


@router.post('/refresh-token', response_model=schemas.TokensResponseSchema)
def refresh_token(db: Session = Depends(get_db), token: str = Body(...)):
    try:
        payload = jwt.decode(token, config.JWT_REFRESH_SECRET_KEY, algorithms=[security.ALGORITHM], options={'verify_exp': False})
        token_data = schemas.TokenPayload(**payload)

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
    user_data = db_user.__dict__
    return {
        "access_token": security.create_access_token(user_data['username']),
        "refresh_token": token
    }


@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db), admin_user: schemas.UserRead = Depends(is_superuser)):
    try:
        if crud.delete_user(db, user_id=user_id):
            return f'User with id = {user_id} was successfully deleted'
        else:
            raise HTTPException(status_code=404, detail="User not found")
    except exc.IntegrityError as err:
        err_msg = str(err.orig).split(':')[-1].replace('\n', '').strip()
        raise HTTPException(status_code=400, detail=err_msg)


@router.get("/", response_model=list[schemas.UserInfo])
def get_full_users_info(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), admin_user: schemas.UserRead = Depends(is_superuser)):
    return crud.get_users(db, skip=skip, limit=limit)


@router.get("/{user_id}", response_model=schemas.UserRead)
def get_small_info_about_any_user(user_id: int, db: Session = Depends(get_db)):
    if not (db_user := crud.get_user(db, user_id=user_id)):
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@router.get("/me/{user_id}", response_model=schemas.UserInfo)
def get_info_about_me(user_id: int, current_user: schemas.UserRead = Depends(get_current_user), db: Session = Depends(get_db)):
    username = current_user.username
    if user_id == current_user.id:
        return crud.get_info_about_me(db, username=username)
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No permissions",
        )


@router.patch("/{user_id}")
def update_item(user_id: int, user: schemas.UserUpdate, db: Session = Depends(get_db),  current_user: schemas.UserRead = Depends(get_current_user)):
    try:
        if crud.update_user(db, user_id=user_id, user=user):
            return f'Row with id = {user_id} was successfully updated'
        else:
            raise HTTPException(status_code=404, detail="User not found")
    except exc.IntegrityError as err:
        err_msg = str(err.orig).split(':')[-1].replace('\n', '').strip()
        raise HTTPException(status_code=400, detail=err_msg)
