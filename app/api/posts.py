from flask import request
from app import db

from app.api import bp
from app.api.errors import success_response, error_response
from app.api.auth import token_auth
from app.models import Post

@bp.route('/posts', methods=['GET'])
@token_auth.login_required
def get_posts():
    posts = Post.query.all()
    data = [post.to_dict() for post in posts]
    return success_response(200, data)

@bp.route('/posts/<int:id>', methods=['GET'])
@token_auth.login_required
def get_post(id):
    post = Post.query.get(id)
    if post is None:
        return error_response(404, f'Post id {id} not found')
    data = post.to_dict()
    return success_response(200, data)

@bp.route('/posts', methods=['POST'])
@token_auth.login_required
def create_post():
    data = request.get_json()
    if 'body' not in data:
        return error_response(400, 'Missing fields')
    author = token_auth.current_user()
    post = Post()
    post.from_dict(data)
    post.author = author
    db.session.add(post)
    db.session.commit()
    response = post.to_dict()
    return success_response(201, response)
