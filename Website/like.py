from flask import Blueprint, flash, redirect, url_for, request, jsonify
from flask_login import login_required, current_user
from .users_cl import Photo, Like, Comment, db

like = Blueprint('like', __name__)

@like.route('/like/<int:photo_id>', methods=['POST'])
@login_required
def like_photo(photo_id):
    photo = Photo.query.get_or_404(photo_id)
    if not photo:
        return jsonify({'success': False, 'message': 'Photo not found.'})

    like = Like.query.filter_by(user_id=current_user.id, photo_id=photo_id).first()
    if like:
        return jsonify({'success': False, 'message': 'You already liked this photo.'})
    else:
        new_like = Like(user_id=current_user.id, photo_id=photo_id)
        db.session.add(new_like)
        db.session.commit()
        return jsonify({'success': True, 'liked': True})

@like.route('/unlike/<int:photo_id>', methods=['POST'])
@login_required
def unlike_photo(photo_id):
    photo = Photo.query.get_or_404(photo_id)
    if not photo:
        return jsonify({'success': False, 'message': 'Photo not found.'})

    like = Like.query.filter_by(user_id=current_user.id, photo_id=photo_id).first()
    if like:
        db.session.delete(like)
        db.session.commit()
        return jsonify({'success': True, 'liked': False})
    else:
        return jsonify({'success': False, 'message': 'You have not liked this photo.'})

@like.route('/comment/<int:photo_id>', methods=['POST'])
@login_required
def comment_photo(photo_id):
    photo = Photo.query.get_or_404(photo_id)
    if not photo:
        return jsonify({'success': False, 'message': 'Photo not found.'})

    text = request.form.get('text')
    if not text:
        return jsonify({'success': False, 'message': 'Comment cannot be empty.'})
    else:
        new_comment = Comment(user_id=current_user.id, photo_id=photo_id, text=text)
        db.session.add(new_comment)
        db.session.commit()
        return jsonify({'success': True, 'comment': {
            'id': new_comment.id,
            'user_id': new_comment.user_id,
            'user': {'username': current_user.username},
            'text': new_comment.text,
            'timestamp': new_comment.timestamp
        }})

@like.route('/delete_comment/<int:comment_id>', methods=['POST'])
@login_required
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    if comment.user_id != current_user.id:
        return jsonify({'success': False, 'message': 'You do not have permission to delete this comment.'})

    db.session.delete(comment)
    db.session.commit()
    return jsonify({'success': True})