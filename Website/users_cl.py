from . import db
from flask_login import UserMixin

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(50), nullable=False)
    comments = db.relationship('Comment', backref='user', lazy='dynamic')
    likes = db.relationship('Like', backref='user', lazy='dynamic')

class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    photo_id = db.Column(db.Integer, db.ForeignKey('photo.id'), nullable=False)

class Photo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    likes = db.relationship('Like', backref='photo', lazy='dynamic')
    comments = db.relationship('Comment', backref='photo', lazy='dynamic')

    def is_liked_by(self, user):
        return Like.query.filter_by(user_id=user.id, photo_id=self.id).count() > 0

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    photo_id = db.Column(db.Integer, db.ForeignKey('photo.id'), nullable=False)
    text = db.Column(db.String(500), nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp(), nullable=False)