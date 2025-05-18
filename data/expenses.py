import datetime
import sqlalchemy as sa
from sqlalchemy.orm import relationship
from .db_session import SqlAlchemyBase


class Expense(SqlAlchemyBase):
    __tablename__ = 'expenses'

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    amount = sa.Column(sa.Float, nullable=False)
    date = sa.Column(sa.DateTime, default=datetime.datetime.utcnow)
    comment = sa.Column(sa.String, nullable=True)

    user_id = sa.Column(sa.Integer, sa.ForeignKey("users.id"))
    user = relationship("User", back_populates="expenses")

    category_id = sa.Column(sa.Integer, sa.ForeignKey("categories.id"), nullable=True)
    category = relationship("Category", back_populates="expenses")
