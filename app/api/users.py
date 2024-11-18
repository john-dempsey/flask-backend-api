import sqlalchemy as sa
from flask import request, url_for, abort
from app import db
from app.models import User
from app.api import bp
from app.api.auth import token_auth
from app.api.errors import success_response, error_response

@bp.route('/users/<int:id>', methods=['GET'])
@token_auth.login_required
def get_user(id):
    user = User.query.get(id)
    if user is None:
        return error_response(404, f'User id {id} not found')
    include_email = token_auth.current_user().id == id
    data = user.to_dict(include_email)
    return success_response(200, data)

@bp.route('/users', methods=['GET'])
@token_auth.login_required
def get_users():
    users = User.query.all()
    data = [user.to_dict() for user in users]
    return success_response(200, data)

@bp.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    if 'username' not in data or 'email' not in data or 'password' not in data:
        return error_response(400, 'Missing fields')
    errors = {}
    if db.session.scalar(sa.select(User).where(
            User.username == data['username'])):
        errors['username'] = 'Please use a different username'
    if db.session.scalar(sa.select(User).where(
            User.email == data['email'])):
        errors['email'] = 'Please use a different email address'
    if errors:
        return error_response(400, errors)
    user = User()
    user.from_dict(data, new_user=True)
    db.session.add(user)
    db.session.commit()
    data = user.to_dict(include_email=True)
    return success_response(201, data)

@bp.route('/users/<int:id>', methods=['PUT'])
@token_auth.login_required
def update_user(id):
    if token_auth.current_user().id != id:
        return error_response(403)
    user = User.query.get(id)
    if user is None:
        return error_response(404, f'User id {id} not found')
    data = request.get_json()
    errors = {}
    if 'username' in data and data['username'] != user.username and \
        db.session.scalar(sa.select(User).where(
            User.username == data['username'])):
        errors['username'] = 'Please use a different username'
    if 'email' in data and data['email'] != user.email and \
        db.session.scalar(sa.select(User).where(
            User.email == data['email'])):
        errors['email'] = 'Please use a different email address'
    if errors:
        return error_response(400, errors)
    user.from_dict(data, new_user=False)
    db.session.commit()
    data = user.to_dict(include_email=True)
    return success_response(200, data)