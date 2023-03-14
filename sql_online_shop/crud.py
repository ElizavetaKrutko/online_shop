from sqlalchemy.orm import Session
from . import models, schemas
from typing import Union, Any
import utils


def get_category(db: Session, category_id: int):
    return db.query(models.Category).filter(models.Category.id == category_id).first()


def get_category_child_list(db: Session, category_id: int):
    db_category = db.query(models.Category).filter(models.Category.id == category_id).first()
    db_category.child_categories = list(db.query(models.Category).with_entities(
        models.Category.id, models.Category.name).filter(models.Category.parent_category_id == category_id))
    return db_category


def get_categories(db: Session, skip: int = 0, limit: int = 100):
    db_categories = db.query(models.Category).offset(skip).limit(limit).all()
    return db_categories


def create_category(db: Session, category: schemas.CategoryCreate):
    db_category = models.Category(name=category.name, parent_category_id=category.parent_category_id)
    db.add(db_category)
    db.commit()
    return db_category


def delete_category(db: Session, category_id: int):
    db_category = db.query(models.Category).filter(models.Category.id == category_id).delete()
    db.commit()
    return db_category


def update_category(db: Session, category_id: int, category: schemas.CategoryUpdate):
    db_category = db.query(models.Category).filter(models.Category.id == category_id)
    if db_category.first():
        if category.name:
            db_category.update({models.Category.name: category.name}, synchronize_session=False)
        if category.parent_category_id:
            db_category.update({models.Category.parent_category_id: category.parent_category_id}, synchronize_session=False)
        db.commit()
        return db_category


# crud for items
def create_category_item(db: Session, item: schemas.ItemBase):
    db_item = models.Item(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def delete_category_item(db: Session, item_id: int):
    db_item = db.query(models.Item).filter(models.Item.id == item_id).delete()
    db.commit()
    return db_item


def update_item(db: Session, item_id: int, item: schemas.ItemUpdate):
    item_dict = item.dict(exclude_unset=True)
    db_item_query = db.query(models.Item).filter(models.Item.id == item_id)
    db_item = db_item_query.first()
    if db_item:
        db_item_query.filter(models.Item.id == item_id).update(item_dict,synchronize_session=False)
        db.commit()
        db.refresh(db_item)
        return db_item


def get_item(db: Session, item_id: int):
    return db.query(models.Item).filter(models.Item.id == item_id).first()


def get_items(db: Session, item_category_id: Union[list, None], skip: int = 0, limit: int = 100):
    if item_category_id:
        item_category_id_list = item_category_id[0].split(',')
        return db.query(models.Item).filter(models.Item.item_category_id.in_(item_category_id_list)).offset(skip).limit(
                limit).all()
    else:
        return db.query(models.Item).offset(skip).limit(limit).all()


# USERS
def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = utils.get_password_hash(user.password)
    user_data = user.dict()
    del user_data["password"]
    user_data["hashed_password"] = hashed_password
    db_user = models.User(**user_data)
    db.add(db_user)
    db.commit()
    return db_user


def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def delete_user(db: Session, user_id: int):
    db_user = db.query(models.User).filter(models.User.id == user_id).delete()
    db.commit()
    return db_user


def update_user(db: Session, user_id: int, user: schemas.UserUpdate):
    print(type(user))
    user_dict = user.dict(exclude_unset=True)
    db_user_query = db.query(models.User).filter(models.User.id == user_id)
    db_user = db_user_query.first()
    if db_user:
        db_user_query.filter(models.User.id == user_id).update(user_dict, synchronize_session=False)
        db.commit()
        db.refresh(db_user)
        return db_user


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    db_users = db.query(models.User).offset(skip).limit(limit).all()
    return db_users


def get_info_about_me(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()
