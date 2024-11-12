from faker import Faker
from datetime import timezone

from flask import Blueprint

bp = Blueprint('cli', __name__, cli_group=None)

from app import db
from app.models import User, Post

@bp.cli.command("seed-db")
def seed_db():
    faker = Faker('en_IE')
    num_users = 10
    for _ in range(num_users):
        data = dict(
            username=faker.user_name(),
            email=faker.email(),
            password="secret",
            about_me=faker.text()
        )
        user = User()
        user.from_dict(data, new_user=True)
        db.session.add(user)
    
    num_posts = 100
    for _ in range(num_posts):
        data = dict(
            body=faker.text(),
            timestamp=faker.date_time_this_year(tzinfo=timezone.utc),
            author=User.query.get(faker.random_int(min=1, max=num_users))
        )
        post = Post()
        post.from_dict(data)
        db.session.add(post)
    
    db.session.commit()
