from app import db
from app.api import bp
from app.api.auth import basic_auth, token_auth
from app.api.errors import success_response, error_response

@bp.route('/tokens', methods=['POST'])
@basic_auth.login_required
def user_login():
    token = basic_auth.current_user().get_token()
    db.session.commit()
    return success_response(200, {'token': token})


@bp.route('/tokens', methods=['DELETE'])
@token_auth.login_required
def user_logout():
    token_auth.current_user().revoke_token()
    db.session.commit()
    return success_response(204)
