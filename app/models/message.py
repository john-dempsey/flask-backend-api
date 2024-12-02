from datetime import datetime, timezone

import sqlalchemy as sa
import sqlalchemy.orm as so

from app import db
from app.models.user import User

class Message(db.Model):
    id:           so.Mapped[int]      = so.mapped_column(primary_key=True)
    sender_id:    so.Mapped[int]      = so.mapped_column(sa.ForeignKey(User.id), index=True)
    recipient_id: so.Mapped[int]      = so.mapped_column(sa.ForeignKey(User.id), index=True)
    body:         so.Mapped[str]      = so.mapped_column(sa.String(140))
    timestamp:    so.Mapped[datetime] = so.mapped_column(index=True, default=lambda: datetime.now(timezone.utc))
    author:       so.Mapped[User]     = so.relationship(foreign_keys='Message.sender_id', back_populates='messages_sent')
    recipient:    so.Mapped[User]     = so.relationship(foreign_keys='Message.recipient_id', back_populates='messages_received')

    def __repr__(self):
        return '<Message {}>'.format(self.body)
    
    def from_dict(self, data):
        for field in ['body', 'timestamp', 'sender_id', 'recipient_id']:
            if field in data:
                setattr(self, field, data[field])

    def to_dict(self):
        data = {
            'id': self.id,
            'body': self.body,
            'timestamp': self.timestamp.isoformat() + 'Z',
            'sender': {
                'id' : self.sender_id,
                'username': self.author.username
            },
            'recipient': {
                'id': self.recipient_id,
                'username': self.recipient.username
            }
        }
        return data