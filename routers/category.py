from fastapi import APIRouter
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from sql_online_shop import crud, schemas
from dependencies import get_db, is_superuser
from sqlalchemy import exc
from utils import create_tree

router = APIRouter(
    prefix="/api/v1/categories",
    tags=["categories"],
)


@router.post("/", response_model=schemas.Category)
def create_category(category: schemas.CategoryCreate, db: Session = Depends(get_db), admin_user: schemas.UserRead = Depends(is_superuser)):
    try:
        return crud.create_category(db=db, category=category)
    except exc.IntegrityError as err:
        err_msg = str(err.orig).split(':')[-1].replace('\n', '').strip()
        raise HTTPException(status_code=400, detail=err_msg)


@router.get("/", response_model=list[schemas.Category])
def get_categories(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    categories = crud.get_categories(db, skip=skip, limit=limit)
    copied_categories = [i.__dict__ for i in categories]
    return create_tree(copied_categories, None, {"key": "id", "parentKey": "parent_category_id", "children_path": "child_categories"})


@router.get("/{category_id}", response_model=schemas.Category)
def get_category_child_list(category_id: int, db: Session = Depends(get_db)):
    if not (db_category := crud.get_category_child_list(db, category_id=category_id)):
        raise HTTPException(status_code=404, detail="Category not found")
    return db_category


@router.delete("/{category_id}")
def delete_category(category_id: int, db: Session = Depends(get_db), admin_user: schemas.UserRead = Depends(is_superuser)):
    try:
        if crud.delete_category(db, category_id=category_id):
            return f'Row with id = {category_id} was successfully deleted'
        else:
            raise HTTPException(status_code=404, detail="Record not found")
    except exc.IntegrityError as err:
        err_msg = str(err.orig).split(':')[-1].replace('\n', '').strip()
        raise HTTPException(status_code=400, detail=err_msg)


@router.patch("/{category_id}")
def update_category(category_id: int, category: schemas.CategoryUpdate, db: Session = Depends(get_db), admin_user: schemas.UserRead = Depends(is_superuser)):
    if crud.update_category(db, category_id=category_id, category=category):
        return f'Row with id = {category_id} was successfully updated'
    else:
        raise HTTPException(status_code=404, detail="Category not found")
