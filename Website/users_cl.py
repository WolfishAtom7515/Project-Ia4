from . import db
from flask_login import UserMixin


class User(db.Model, UserMixin):
    id       = db.Column(db.Integer   , primary_key=True)
    email    = db.Column(db.String(50), unique=True , nullable=False)
    password = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(50), nullable=False)
