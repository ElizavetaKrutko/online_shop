from fastapi import APIRouter, Query, Depends, HTTPException
from sqlalchemy.orm import Session
from sql_online_shop import crud, schemas
from dependencies import get_db, is_superuser
from sqlalchemy import exc
from typing import Union


router = APIRouter(
    prefix="/api/v1/items",
    tags=["items"],
)


@router.post("/", response_model=schemas.Item)
def create_category_item(item: schemas.ItemBase, db: Session = Depends(get_db), admin_user: schemas.UserRead = Depends(is_superuser)):
    try:
        return crud.create_category_item(db=db, item=item)
    except exc.IntegrityError as err:
        err_msg = str(err.orig).split(':')[-1].replace('\n', '').strip()
        raise HTTPException(status_code=400, detail=err_msg)


@router.delete("/{item_id}")
def delete_category_item(item_id: int, db: Session = Depends(get_db), admin_user: schemas.UserRead = Depends(is_superuser)):
    try:
        if crud.delete_category_item(db, item_id=item_id):
            return f'Row with id = {item_id} was successfully deleted'
        else:
            raise HTTPException(status_code=404, detail="Record not found")
    except exc.IntegrityError as err:
        err_msg = str(err.orig).split(':')[-1].replace('\n', '').strip()
        raise HTTPException(status_code=400, detail=err_msg)


@router.patch("/{item_id}")
def update_item(item_id: int, item: schemas.ItemUpdate, db: Session = Depends(get_db), admin_user: schemas.UserRead = Depends(is_superuser)):
    try:
        if crud.update_item(db, item_id=item_id, item=item):
            return f'Row with id = {item_id} was successfully updated'
        else:
            raise HTTPException(status_code=404, detail="Item not found")
    except exc.IntegrityError as err:
        err_msg = str(err.orig).split(':')[-1].replace('\n', '').strip()
        raise HTTPException(status_code=400, detail=err_msg)


@router.get("/{item_id}", response_model=schemas.Item)
def get_item(item_id: int, db: Session = Depends(get_db)):
    if not (db_item := crud.get_item(db, item_id=item_id)):
        raise HTTPException(status_code=404, detail="Item not found")
    return db_item


@router.get("/", response_model=list[schemas.Item])
def get_items(item_category_id: Union[list, None] = Query(default=None),
              skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    try:
        if (db_item := crud.get_items(db, skip=skip, limit=limit, item_category_id=item_category_id)) == []:
            raise HTTPException(status_code=404, detail="Item category not found")
        else:
            return db_item
    except exc.IntegrityError as err:
        err_msg = str(err.orig).split(':')[-1].replace('\n', '').strip()
        raise HTTPException(status_code=400, detail=err_msg)
