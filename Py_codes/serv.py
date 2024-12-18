from flask import Blueprint, flash, render_template, request, redirect, url_for, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from PIL import Image 
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

            # Create and save the thumbnail
            thumbnail_filename = f"{filename.rsplit('.', 1)[0]}.thumb.{ext}"
            thumbnail_path = os.path.join(category_folder, thumbnail_filename)
            create_thumbnail(file_path, thumbnail_path, (200, 200))

            flash('File successfully uploaded', 'success')
            return redirect(url_for('serv.gallery', username=username))

    images = os.listdir(user_folder)
    return render_template("gallery.html", user=current_user, images=images, upload_folder=user_folder)



@serv.route('/browse')
def browse():
    categories_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], 'Categories')
    if not os.path.exists(categories_folder):
        os.makedirs(categories_folder)

    categories = [d for d in os.listdir(categories_folder) if os.path.isdir(os.path.join(categories_folder, d))]
    random.shuffle(categories)

    images_by_category = {}
    for category in categories:
        category_path = os.path.join(categories_folder, category)
        images = [f for f in os.listdir(category_path) if allowed_file(f)]
        images_by_category[category] = images

    return render_template("browse.html", user=current_user, images_by_category=images_by_category)


def create_thumbnail(input_image_path, output_image_path, size):
    with Image.open(input_image_path) as image:
        image.thumbnail(size)
        image.save(output_image_path)
