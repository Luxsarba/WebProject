import datetime
import sqlalchemy as sa
from sqlalchemy.orm import relationship
from .db_session import SqlAlchemyBase


class User(SqlAlchemyBase):
    __tablename__ = 'users'

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=False)
    username = sa.Column(sa.String, nullable=True)
    created_date = sa.Column(sa.DateTime, default=datetime.datetime.utcnow)

    expenses = relationship("Expense", back_populates="user")
    categories = relationship("Category", back_populates="user")
