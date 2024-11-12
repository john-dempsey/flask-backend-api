from werkzeug.http import HTTP_STATUS_CODES
from werkzeug.exceptions import HTTPException
from app.api import bp

def success_response(status_code, data=None, message=None):
    payload = {
        'success': True,
        'message': message or HTTP_STATUS_CODES.get(status_code, 'Success'),
        'data': data or {}
    }
    return payload, status_code

def error_response(status_code, data=None):
    payload = {
        'success': False,
        'message': HTTP_STATUS_CODES.get(status_code, 'Unknown error'),
        'data': data or {}
    }
    return payload, status_code

def bad_request(message):
    return error_response(400, message)

@bp.errorhandler(HTTPException)
def handle_exception(e):
    return error_response(500, e.code)

@bp.app_errorhandler(404)
def not_found_error(error):
    return error_response(404, error.description)

@bp.app_errorhandler(500)
def not_found_error(error):
    return error_response(500, error.description)