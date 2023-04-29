import datetime
import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy import orm
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin


class Applications(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'applications'
    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    customer_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("customers.id"))
    transport_id = sqlalchemy.Column(sqlalchemy.Integer,
                                    sqlalchemy.ForeignKey("transport.id"))
    dispatcher_id = sqlalchemy.Column(sqlalchemy.Integer,
                                     sqlalchemy.ForeignKey("dispatchers.id"))
    task = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    start = sqlalchemy.Column(sqlalchemy.DateTime)
    end = sqlalchemy.Column(sqlalchemy.DateTime)
    reviewed = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    accepted = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    completed = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    customer = orm.relationship('Customer')
    transport = orm.relationship('Transport')
