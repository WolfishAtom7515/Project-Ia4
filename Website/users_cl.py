from flask import current_app
from . import db
from flask_login import UserMixin
from datetime import datetime
from .encryption import encrypt_message, decrypt_message
import os
import json

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

class Chat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    users = db.relationship('User', secondary='chat_user', backref='chats')

    def get_chat_directory(self):
        base_dir = current_app.config['CHAT_FOLDER']
        return os.path.join(base_dir, str(self.id))

    def get_messages(self):
        chat_dir = self.get_chat_directory()
        chat_file = os.path.join(chat_dir, 'messages.json')
        if not os.path.exists(chat_file):
            return []
        messages = []
        with open(chat_file, 'r') as f:
            for line in f:
                if line.strip():
                    message = json.loads(line.strip())
                    message['timestamp'] = datetime.fromisoformat(message['timestamp']).strftime('%H:%M %d-%m-%Y')
                    decrypted_message = decrypt_message(message['content'])
                    message['content'] = decrypted_message
                    messages.append(message)
        return messages

    def add_message(self, user_id, content):
        chat_dir = self.get_chat_directory()
        if not os.path.exists(chat_dir):
            os.makedirs(chat_dir)
        chat_file = os.path.join(chat_dir, 'messages.json')
        timestamp = datetime.utcnow().isoformat()
        message = {
            'user_id': user_id,
            'content': content,
            'timestamp': timestamp
        }
        with open(chat_file, 'a') as f:
            f.write(json.dumps(message) + '\n')

chat_user = db.Table('chat_user',
    db.Column('chat_id', db.Integer, db.ForeignKey('chat.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
)
