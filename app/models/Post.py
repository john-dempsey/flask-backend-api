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
    comments: so.WriteOnlyMapped['Comment'] = so.relationship('Comment', back_populates='post')

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
            'author': self.author.username,
            'tags': [tag.name for tag in self.get_tags()],
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
    
    def add_comment(self, comment):
        if not self.has_comment(comment):
            self.comments.add(comment)
    
    def remove_comment(self, comment):
        if self.has_comment(comment):
            self.comments.remove(comment)

    def has_comment(self, comment):
        return comment in db.session.scalars(self.comments.select())
    
    def get_comments(self):
        return db.session.scalars(self.comments.select()).all()

from app.models.tag import Tag, post_tag
from app.models.comment import Comment