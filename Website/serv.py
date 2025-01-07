from flask import Blueprint, flash, render_template, request, redirect, url_for, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from PIL import Image 
from .users_cl import User, Chat, Photo, db
from .recommendation_system import create_dataset, find_3rd_nearest_neighbours, create_users, generate_recs, photo_mappings
from . import db
import random
import os

serv = Blueprint('serv', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@serv.route('/')
@login_required
def home():
    return render_template("home.html", user=current_user)

@serv.route('/about_me')
@login_required
def about_me():
    return render_template("about_me.html", user=current_user)

@serv.route('/gallery/<username>', methods=['GET', 'POST'])
@login_required
def gallery(username):
    user_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], username)
    if not os.path.exists(user_folder):
        os.makedirs(user_folder)

    if request.method == 'POST' and 'file' in request.files:
        file = request.files['file']
        categories = request.form.get('categories')
        photo_name = request.form.get('photo_name')

        if file.filename == '':
            flash('No selected file', 'error')
        elif not allowed_file(file.filename):
            flash('Only PNG and JPG files are allowed', 'error')
        elif not categories:
            flash('Category field must be filled', 'error')
        else:
            filename = secure_filename(file.filename)

            if '.' in filename:
                ext = filename.rsplit('.', 1)[1]
            else:
                ext = 'jpg'  

            if photo_name:
                filename = f"{secure_filename(photo_name)}.{ext}"

            file_path = os.path.join(user_folder, filename)
            file.seek(0)
            file.save(file_path)

            categories_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], 'Categories')
            if not os.path.exists(categories_folder):
                os.makedirs(categories_folder)

            category_folder = os.path.join(categories_folder, secure_filename(categories))
            if not os.path.exists(category_folder):
                os.makedirs(category_folder)
            
            category_file_path = os.path.join(category_folder, filename)
            file.seek(0)
            file.save(category_file_path)

            thumbnail_filename = f"{filename.rsplit('.', 1)[0]}.thumb.{ext}"
            thumbnail_path = os.path.join(category_folder, thumbnail_filename)
            create_thumbnail(file_path, thumbnail_path, (200, 200))

            # Save photo to database
            new_photo = Photo(filename=filename, category=categories)
            db.session.add(new_photo)
            db.session.commit()

            # Debugging: Print saved photo details
            print(f"Saved Photo: {new_photo}")

            flash('File successfully uploaded', 'success')
            return redirect(url_for('serv.gallery', username=username))

    images = os.listdir(user_folder)
    return render_template("gallery.html", user=current_user, images=images, upload_folder=user_folder)

@serv.route('/for_you')
@login_required
def for_you():
    # generate recommendations
    create_users()
    [users, recs_matrix] = create_dataset()
    [similarities, similar_users] = find_3rd_nearest_neighbours(users, recs_matrix)
    recs = generate_recs(users, recs_matrix, similarities, similar_users)
    [photos, photo_dict] = photo_mappings()

    recommended_photos = []
    for photo_index in recs.keys():
        # photo_id = photo_dict[photo_index]
        photo_id = list(photo_dict.keys())[list(photo_dict.values()).index(photo_index)]
        photo_name = Photo.query.filter_by(id=photo_id).first().filename
        photo_category = Photo.query.filter_by(id=photo_id).first().category
        filepath = os.path.join(photo_category, photo_name)
        recommended_photos.append(filepath)
    
    return render_template("for_you.html", user=current_user, images=recommended_photos)

@serv.route('/browse')
@login_required
def browse():
    categories_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], 'Categories')
    if not os.path.exists(categories_folder):
        os.makedirs(categories_folder)

    categories = [d for d in os.listdir(categories_folder) if os.path.isdir(os.path.join(categories_folder, d))]

    random.shuffle(categories)
    images_by_category = {}

    for category in categories:
        category_path = os.path.join(categories_folder, category)
        image_filenames = [f for f in os.listdir(category_path) if allowed_file(f)]
        print(f"Category: {category}, Image filenames: {image_filenames}")  # Debugging: Print image filenames
        images = Photo.query.filter_by(category=category).filter(Photo.filename.in_(image_filenames)).all()
        print(f"Category: {category}, Images: {images}")  # Debugging: Print images
        images_by_category[category] = images

    # Debugging: Print images_by_category
    print("Images by category:", images_by_category)

    return render_template("browse.html", user=current_user, images_by_category=images_by_category)

@serv.route('/debug_photos')
@login_required
def debug_photos():
    photos = Photo.query.all()
    print("YESSS")
    for photo in photos:
        print(f"Photo ID: {photo.id}, Filename: {photo.filename}, Category: {photo.category}")
    return "Check the logs for photo details."

@serv.route('/messages')
@login_required
def messages():
    chats = Chat.query.filter(Chat.users.any(id=current_user.id)).all()
    for chat in chats:
        messages = chat.get_messages()
        last_message = messages[-1] if messages else None
        chat.last_message_time = last_message['timestamp'] if last_message else None
        chat.last_message_preview = last_message['content'] if last_message else "No messages yet"
        chat.last_message_sender = User.query.get(last_message['user_id']).username if last_message else "N/A"
        other_user = next(user for user in chat.users if user.id != current_user.id)
        chat.display_title = f"Chat with {other_user.username}"
    return render_template('messages.html', chats=chats)

@serv.route('/chat/<int:chat_id>')
@login_required
def chat(chat_id):
    chat = Chat.query.get_or_404(chat_id)
    messages = chat.get_messages()
    for message in messages:
        message['username'] = User.query.get(message['user_id']).username
    other_user = next(user for user in chat.users if user.id != current_user.id)
    chat.display_title = f"Chat with {other_user.username}"
    return render_template('chat.html', chat=chat, messages=messages)

@serv.route('/chat/<int:chat_id>/send', methods=['POST'])
@login_required
def send_message(chat_id):
    content = request.form['content']
    chat = Chat.query.get_or_404(chat_id)
    chat.add_message(user_id=current_user.id, content=content)
    return redirect(url_for('serv.chat', chat_id=chat_id))

@serv.route('/new_chat', methods=['GET', 'POST'])
@login_required
def new_chat():
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        user = User.query.get(user_id)
        if user:
            chat = Chat(title=f"Chat with {user.username}")
            chat.users.append(current_user)
            chat.users.append(user)
            db.session.add(chat)
            db.session.commit()
            return redirect(url_for('serv.chat', chat_id=chat.id))
        else:
            flash('User not found', 'error')
    users = User.query.filter(User.id != current_user.id).all()
    return render_template('new_chat.html', users=users)


def create_thumbnail(input_image_path, output_image_path, size):
    with Image.open(input_image_path) as image:
        image.thumbnail(size)
        image.save(output_image_path)