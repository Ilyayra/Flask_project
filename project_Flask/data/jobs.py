import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin


class Jobs(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'jobs'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    director = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'))
    title = sqlalchemy.Column(sqlalchemy.String)
    description = sqlalchemy.Column(sqlalchemy.Text)
    pay = sqlalchemy.Column(sqlalchemy.Integer)
    start_date = sqlalchemy.Column(sqlalchemy.DateTime)
    image = sqlalchemy.Column(sqlalchemy.String, default='0')
    directorref = orm.relation("User")
