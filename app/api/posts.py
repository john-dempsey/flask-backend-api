from app.api import bp
from app.api.errors import success_response, error_response

from app.models import Post

@bp.route('/posts', methods=['GET'])
def get_posts():
    posts = Post.query.all()
    data = [post.to_dict() for post in posts]
    return success_response(200, data)

@bp.route('/posts/<int:id>', methods=['GET'])
def get_post(id):
    post = Post.query.get(id)
    if post is None:
        return error_response(404, f'Post id {id} not found')
    data = post.to_dict()
    return success_response(200, data)
