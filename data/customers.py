import datetime
import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy import orm
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin


class Customer(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'customers'
    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    dispatcher_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("dispatchers.id"))
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    job_title = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    tel = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    email = sqlalchemy.Column(sqlalchemy.String,
                              index=True, unique=True, nullable=True)
    password = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    applications = orm.relationship("Applications", back_populates='customer')
    dispatcher = orm.relationship('Dispatcher')

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)