from faker import Faker
from datetime import timezone

from flask import Blueprint

bp = Blueprint('cli', __name__, cli_group=None)

from app import db
from app.models import User, Post, Tag

@bp.cli.command("seed-db")
def seed_db():
    faker = Faker('en_IE')

    db.drop_all()
    db.create_all()

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

    tags = [
        "Startup", "Life", "Blockchain", "Poetry", "Life Lessons", "Politics", "Health",
        "Love", "Travel", "Technology", "Entrepreneurship", "Self Improvement", "Education", "Writing",
        "Business", "Cryptocurrency", "Design", "Social Media", "Music", "Relationships", "Wildlife",
        "Sports", "Mental Health", "Productivity", "Programming", "Food", "Leadership", "Javascript", 
        "Art", "Fiction", "Humor", "Artificial Intelligence", "UX", "Culture", "Books",
        "Photography", "Creativity", "Data Science", "Psychology", "Software Development", "Self", "Family",
        "Marketing", "Fitness", "History", "Fashion", "Gaming", "Science", "Film", "Motivation"
    ]
    for tag in tags:
        t = Tag(name=tag)
        db.session.add(t)
    
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
        num_tags = faker.random_int(min=1, max=5)
        for _ in range(num_tags):
            post.add_tag(Tag.query.get(faker.random_int(min=1, max=len(tags))))
    
    db.session.commit()
