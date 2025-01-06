import numpy as np
import pandas as pd
from .users_cl import Photo, Like, Comment, User, db
from flask_login import current_user
from werkzeug.security import generate_password_hash
import _sqlite3
import csv
import os

# function for mapping the user index to the user id from the database
def user_mappings():
    users_tuples = User.query.with_entities(User.id).all()
    users = [item[0] for item in users_tuples]

    user_dict = {}
    user_idx = 0
    for user in users:
        user_dict[user] = user_idx
        user_idx += 1
    return [users, user_dict]

# function for mapping the photo index to the photo id from the database
def photo_mappings():
    photos_tuples = Photo.query.with_entities(Photo.id).all()
    photos = [item[0] for item in photos_tuples]

    photo_dict = {}
    photo_idx = 0
    for photo in photos:
        photo_dict[photo] = photo_idx
        photo_idx += 1
    return [photos, photo_dict]

# function for creating the engagement matrix that counts the likelihood of each user engaging with each photo
def create_dataset():
    nr_users = User.query.count()
    nr_photos = Photo.query.count()
    recs_matrix = np.zeros((nr_users, nr_photos))

    [users, user_dict] = user_mappings()
    [photos, photo_dict] = photo_mappings()

    # calculate the engagement of an user to a photo by counting likes and comments 
    likes = Like.query.all()
    for like in likes:
        user_idx = user_dict[like.user_id]
        photo_idx = photo_dict[like.photo_id]
        recs_matrix[user_idx][photo_idx] += 1

    comments = Comment.query.all()
    for comment in comments:
        user_idx = user_dict[comment.user_id]
        photo_idx = photo_dict[comment.photo_id]
        recs_matrix[user_idx][photo_idx] += 1

    return [users, recs_matrix]

# function for generating the most similar 3 users to the current user based on engagement
def find_3rd_nearest_neighbours(users, recs_matrix):
    crt_user_idx = users.index(current_user.id)
    crt_user_array = recs_matrix[crt_user_idx]

    # calculate similarity between current user and all other users
    similarity_arr = np.zeros(len(users))
    crt_norm = np.linalg.norm(crt_user_array)
    for user_idx in range(0, len(users)):
        if user_idx != crt_user_idx:
            norm = np.linalg.norm(recs_matrix[user_idx])
            dot_product = np.dot(crt_user_array, recs_matrix[user_idx])

            if crt_norm == 0 or norm == 0:
                similarity_arr[user_idx] = -1
            else:
                similarity_arr[user_idx] = dot_product / (crt_norm * norm)
        else:
            # assigning -1 to the current user row since it should not be taken into consideration
            similarity_arr[user_idx] = -1

    # get 3 most similar users
    similarities = np.sort(similarity_arr)[::-1][:3]
    # the users that have a low similarity with the current user are substituted by 0
    similarities = similarities[similarities > 0]
    tmp = np.array([0] * (3 - len(similarities)))
    similarities = np.concatenate((similarities, tmp))
    similar_users = np.argsort(similarity_arr)[::-1][:3]

    return [similarities, similar_users]

def generate_recs(users, recs_matrix, similarities, similar_users):
    [photos, photo_dict] = photo_mappings()
    [similarities, similar_users] = find_3rd_nearest_neighbours(users, recs_matrix)
    # get array for current user
    crt_user_idx = users.index(current_user.id)
    crt_user_array = recs_matrix[crt_user_idx]

    # for each photo the user has not engaged to, predict engagement based on most similar users
    possible_recs = np.where(crt_user_array == 0)[0]

    weights = similarities[0] + similarities[1] + similarities[2]
    predictions = {}
    for photo in possible_recs:
        score = recs_matrix[similar_users[0]][photo] * similarities[0] + recs_matrix[similar_users[1]][photo] * similarities[1] + recs_matrix[similar_users[2]][photo] * similarities[2]
        predictions[int(photo)] = float(score / weights)

    # recommended photos are the ones that the user is likely to engage with
    predictions = {key:val for key,val in predictions.items() if val > 0}

    # sort predictions in descending order
    recs = {k: v for k, v in sorted(predictions.items(), key=lambda item: item[1], reverse=True)}
    return recs

def create_users():
    for i in range(0, 10):
        username = "mock_user" + str(i)
        email = username + "@gmail.com"
        password = "123456"
        user = User.query.filter_by(email=email).first()
        if not user:
            new_user = User(email=email, username=username, password=generate_password_hash(password, method='pbkdf2:sha256'))
            db.session.add(new_user)
            db.session.commit()