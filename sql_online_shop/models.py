from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable
from sqlalchemy import Column, ForeignKey, Integer, String, FLOAT, Boolean, DateTime, func
from sqlalchemy.orm import relationship
from sql_online_shop.database import Base


class Category(Base):
    """Category info"""
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True)
    name = Column(String(90), unique=True)
    parent_category_id = Column(Integer, ForeignKey("categories.id", ondelete='RESTRICT'))


class Item(Base):
    """Item info"""
    __tablename__ = "items"

    id = Column(Integer, primary_key=True)
    name = Column(String(90), unique=True)
    unit_price = Column(FLOAT(8))
    amount = Column(Integer)
    item_category_id = Column(Integer, ForeignKey("categories.id", ondelete='RESTRICT'))

    related_category = relationship("Category", backref="items", passive_deletes=True)


class User(Base):
    """User account"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String(90), unique=True)
    username = Column(String(90), unique=True, nullable=False)
    first_name = Column(String(90))
    last_name = Column(String(90))
    registered_at = Column(DateTime(), nullable=False, server_default=func.now())
    hashed_password = Column(String(length=1024), nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
