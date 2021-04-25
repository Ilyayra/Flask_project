import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin


association_table = sqlalchemy.Table('association', SqlAlchemyBase.metadata,
                                     sqlalchemy.Column('chats', sqlalchemy.Integer,
                                                       sqlalchemy.ForeignKey('chats.id')),
                                     sqlalchemy.Column('users', sqlalchemy.Integer,
                                                       sqlalchemy.ForeignKey('users.id')))


class Chat(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'chats'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    usersids = sqlalchemy.Column(sqlalchemy.String)
    text = sqlalchemy.Column(sqlalchemy.Text)
