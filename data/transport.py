import datetime
import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy import orm
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin


class Transport(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'transport'
    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    dispatcher_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("dispatchers.id"))
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    coordinates = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    status = sqlalchemy.Column(sqlalchemy.Boolean, default=True)
    state = sqlalchemy.Column(sqlalchemy.Boolean, default=True)
    dispatcher = orm.relationship('Dispatcher')
