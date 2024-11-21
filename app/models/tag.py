import sqlalchemy as sa
import sqlalchemy.orm as so

from app import db

post_tag = sa.Table(
    'post_tag',
    db.metadata,
    sa.Column('post_id', sa.Integer, sa.ForeignKey('post.id'), primary_key=True),
    sa.Column('tag_id', sa.Integer, sa.ForeignKey('tag.id'), primary_key=True)
)

class Tag(db.Model):
    id:   so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=True)

    posts: so.WriteOnlyMapped['Post'] = so.relationship('Post', secondary=post_tag, 
                                                        back_populates='tags', 
                                                        passive_deletes=True)

    def __repr__(self):
        return '<Tag {}>'.format(self.name)

    def from_dict(self, data):
        for field in ['name']:
            if field in data:
                setattr(self, field, data[field])

    def to_dict(self):
        data = {
            'id': self.id,
            'name': self.name
        }
        return data
    
    def posts_count(self):
        query = sa.select(sa.func.count()).select_from(
            self.posts.select().subquery())
        return db.session.scalar(query)
    
    def get_posts(self):
        return db.session.scalars(self.posts.select()).all()
    

from app.models.post import Post