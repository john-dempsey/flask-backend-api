from typing import Optional
from datetime import datetime, timezone

import sqlalchemy as sa
import sqlalchemy.orm as so

from app import db
from app.models.user import User
from app.models.post import Post

class Comment(db.Model):
    id:        so.Mapped[int] = so.mapped_column(primary_key=True)
    body:      so.Mapped[str] = so.mapped_column(sa.String(140))
    timestamp: so.Mapped[datetime] = so.mapped_column(index=True, 
                                                      default=lambda: datetime.now(timezone.utc))
    post_id:   so.Mapped[int] = so.mapped_column(sa.ForeignKey(Post.id),index=True)
    user_id:   so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id),index=True)

    author: so.Mapped[User] = so.relationship(back_populates='comments')
    post:   so.Mapped[Post] = so.relationship(back_populates='comments')

    def __repr__(self):
        return '<Comment {}>'.format(self.body)

    def from_dict(self, data):
        for field in ['body', 'post', 'author', 'timestamp']:
            if field in data:
                setattr(self, field, data[field])

    def to_dict(self):
        data = {
            'id': self.id,
            'body': self.body,
            'timestamp': self.timestamp.isoformat() + 'Z',
            'post': self.post.id,
            'author': self.author.username
        }
        return data
