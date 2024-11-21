from typing import Optional
from datetime import datetime, timezone

import sqlalchemy as sa
import sqlalchemy.orm as so

from app import db
from app.models.user import User

class Post(db.Model):
    id:        so.Mapped[int] = so.mapped_column(primary_key=True)
    body:      so.Mapped[str] = so.mapped_column(sa.String(140))
    timestamp: so.Mapped[datetime] = so.mapped_column(index=True, 
                                                      default=lambda: datetime.now(timezone.utc))
    user_id:   so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id),index=True)

    author: so.Mapped[User] = so.relationship(back_populates='posts')
    tags:   so.WriteOnlyMapped['Tag'] = so.relationship('Tag', secondary='post_tag', 
                                                        back_populates='posts', 
                                                        passive_deletes=True)

    def __repr__(self):
        return '<Post {}>'.format(self.body)

    def from_dict(self, data):
        for field in ['body', 'author', 'timestamp']:
            if field in data:
                setattr(self, field, data[field])

    def to_dict(self):
        data = {
            'id': self.id,
            'body': self.body,
            'timestamp': self.timestamp.isoformat() + 'Z',
            'author': self.author.username
        }
        return data

    def add_tag(self, tag):
        if not self.has_tag(tag):
            self.tags.add(tag)
    
    def remove_tag(self, tag):
        if self.has_tag(tag):
            self.tags.remove(tag)

    def has_tag(self, tag):
        return tag in db.session.scalars(self.tags.select())
    
    def get_tags(self):
        return db.session.scalars(self.tags.select()).all()

from app.models.tag import Tag, post_tag