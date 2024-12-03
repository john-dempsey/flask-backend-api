from datetime import datetime, timezone

from flask import request, render_template, current_app
from app import db
from app.email import send_email
from app.api import bp
from app.api.errors import success_response, error_response
from app.api.auth import token_auth
from app.models import Post, Comment

@bp.route('/posts/<int:pid>/comments', methods=['GET'])
@token_auth.login_required
def comment_post_index(pid):
    post = Post.query.get(pid)
    if post is None:
        return error_response(404, f'Post id {pid} not found')
    data = [comment.to_dict() for comment in post.get_comments()]   
    return success_response(200, data)

@bp.route('/posts/<int:pid>/comments', methods=['POST'])
@token_auth.login_required
def comment_post_create(pid):
    post = Post.query.get(pid)
    if post is None:
        return error_response(404, f'Post id {pid} not found')
    data = request.get_json()
    if 'body' not in data:
        return error_response(400, 'Missing fields')
    author = token_auth.current_user()
    comment = Comment()
    comment.from_dict(data)
    comment.post = post
    comment.author = author
    db.session.add(comment)
    db.session.commit()
    send_email("New comment on your post", 
               current_app.config['ADMINS'][0], 
               recipients=[post.author.email],
               text_body=render_template('email/posts_comment.txt', comment=comment),
               html_body=render_template('email/posts_comment.html', comment=comment),
               attachments=None, 
               sync=False)
    response = comment.to_dict()
    return success_response(201, response)

@bp.route('/posts/<int:pid>/comments/<int:cid>', methods=['PUT'])
@token_auth.login_required
def comment_post_update(pid, cid):
    post = Post.query.get(pid)
    if post is None:
        return error_response(404, f'Post id {id} not found')
    comment = Comment.query.get(cid)
    if comment is None:
        return error_response(404, f'Comment id {cid} not found')
    if comment.post != post:
        return error_response(404, f'Comment id {cid} not found in post id {pid}')
    user = token_auth.current_user()
    if user != comment.author:
        return error_response(403, 'Permission denied')
    data = request.get_json()
    if 'body' not in data:
        return error_response(400, 'Missing fields')
    comment.body = data['body']
    comment.timestamp = datetime.now(timezone.utc)
    db.session.commit()
    response = comment.to_dict()
    return success_response(201, response)

@bp.route('/posts/<int:pid>/comments/<int:cid>', methods=['DELETE'])
@token_auth.login_required
def comment_post_delete(pid, cid):
    post = Post.query.get(pid)
    if post is None:
        return error_response(404, f'Post id {id} not found')
    comment = Comment.query.get(cid)
    if comment is None:
        return error_response(404, f'Comment id {cid} not found')
    if comment.post != post:
        return error_response(404, f'Comment id {cid} not found in post id {pid}')
    user = token_auth.current_user()
    if user != comment.author:
        return error_response(403, 'Permission denied')
    post.remove_comment(comment)
    db.session.delete(comment)
    db.session.commit()
    return success_response(204, None)

