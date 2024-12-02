from datetime import datetime, timezone

from flask import request
from app import db

from app.api import bp
from app.api.errors import success_response, error_response
from app.api.auth import token_auth
from app.models import Message, User

@bp.route('/messages', methods=['GET'])
@token_auth.login_required
def message_index():
    user = token_auth.current_user()
    user.last_message_read_time = datetime.now(timezone.utc)
    db.session.commit()
    messages = db.session.scalars(user.messages_received.select().order_by(Message.timestamp.desc()))
    data = [message.to_dict() for message in messages]
    return success_response(200, data)

@bp.route('/messages/<int:id>', methods=['GET'])
@token_auth.login_required
def message_show(id):
    user = token_auth.current_user()
    message = Message.query.get(id)
    if message is None:
        return error_response(404, f'Message id {id} not found')
    if user != message.recipient and user != message.author:
        return error_response(403, 'Permission denied')
    return success_response(200, message.to_dict())

@bp.route('/messages', methods=['POST'])
@token_auth.login_required
def message_create():
    data = request.get_json() or {}
    if 'body' not in data or 'recipient_id' not in data:
        return error_response(400, 'Missing fields')
    
    user = token_auth.current_user()
    recipient = User.query.get(data['recipient_id'])
    if recipient is None:
        return error_response(400, 'Recipient not found')
    
    message = Message()
    message.from_dict(data)
    message.author = user
    message.recipient = recipient
    db.session.add(message)
    db.session.commit()
    return success_response(201, message.to_dict())
