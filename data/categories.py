import sqlalchemy as sa
from sqlalchemy.orm import relationship
from .db_session import SqlAlchemyBase


class Category(SqlAlchemyBase):
    __tablename__ = 'categories'

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    name = sa.Column(sa.String, nullable=False)

    user_id = sa.Column(sa.Integer, sa.ForeignKey("users.id"))
    user = relationship("User", back_populates="categories")

    expenses = relationship("Expense", back_populates="category")
