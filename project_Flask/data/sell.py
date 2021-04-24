import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin


class Sell(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'sell'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    seller = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'))
    title = sqlalchemy.Column(sqlalchemy.String)
    description = sqlalchemy.Column(sqlalchemy.Text)
    price = sqlalchemy.Column(sqlalchemy.Integer)
    start_date = sqlalchemy.Column(sqlalchemy.DateTime)
    image = sqlalchemy.Column(sqlalchemy.String, default='0')
    sellerref = orm.relation("User")
