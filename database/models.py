from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref

from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Table


Base = declarative_base()


class UrlMixin:
    url = Column(String, nullable=False, unique=True)


class IdMixin:
    id = Column(Integer, primary_key=True, autoincrement=True)


tag_post = Table(
    "tag_post",
    Base.metadata,
    Column("post_id", Integer, ForeignKey("post.id")),
    Column("tag_id", Integer, ForeignKey("tag.id")),
)


class Writer(Base, UrlMixin, IdMixin):
    __tablename__ = "writer"
    name = Column(String)
    posts = relationship("Post")
    comments = relationship("Comment")


class Post(Base, UrlMixin, IdMixin):
    __tablename__ = "post"
    title = Column(String, nullable=False)
    post_datetime = Column(DateTime, nullable=False)
    post_image_url = Column(String)
    writer_id = Column(Integer, ForeignKey("writer.id"))
    writer = relationship(Writer)
    tags = relationship("Tag", secondary=tag_post)


class Comment(Base):
    __tablename__ = "comment"
    id = Column(Integer, primary_key=True)
    comment_text = Column(Text, nullable=False)
    writer_id = Column(Integer, ForeignKey("writer.id"))
    parent_id = Column(Integer, ForeignKey("comment.id"))
    writer = relationship(Writer)
    parent = relationship('Comment')


class Tag(Base, UrlMixin, IdMixin):
    __tablename__ = "tag"
    name = Column(String)
    posts = relationship(Post, secondary=tag_post)
