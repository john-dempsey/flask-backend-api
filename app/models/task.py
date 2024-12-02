from typing import Optional
import sqlalchemy as sa
import sqlalchemy.orm as so

import rq
import redis
from flask import current_app

from app import db
from app.models.user import User

class Task(db.Model):
    id:          so.Mapped[str]           = so.mapped_column(sa.String(36), primary_key=True)
    name:        so.Mapped[str]           = so.mapped_column(sa.String(128), index=True)
    description: so.Mapped[Optional[str]] = so.mapped_column(sa.String(128))
    user_id:     so.Mapped[int]           = so.mapped_column(sa.ForeignKey(User.id))
    complete:    so.Mapped[bool]          = so.mapped_column(default=False)

    user:        so.Mapped[User]          = so.relationship(back_populates='tasks')

    def get_rq_job(self):
        try:
            rq_job = rq.job.Job.fetch(self.id, connection=current_app.redis)
        except (redis.exceptions.RedisError, rq.exceptions.NoSuchJobError):
            return None
        return rq_job

    def get_progress(self):
        job = self.get_rq_job()
        return job.meta.get('progress', 0) if job is not None else 100