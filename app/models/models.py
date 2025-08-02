from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Index
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Post(Base):
    """Post model representing content posts"""
    __tablename__ = 'post'

    id = Column(Integer, primary_key=True, doc="Unique post identifier")
    text = Column(String, nullable=False, doc="Post text content")
    topic = Column(String, nullable=False, doc="Post topic/category")

    # Relationships
    feed_actions = relationship("Feed", back_populates="post")


class User(Base):
    """User model representing application users"""
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, doc="Unique user identifier")
    gender = Column(Integer, nullable=False,
                    doc="User gender (0=female, 1=male)")
    age = Column(Integer, nullable=False, doc="User age")
    country = Column(String, nullable=False, doc="User country")
    city = Column(String, nullable=False, doc="User city")
    exp_group = Column(Integer, nullable=False,
                       doc="Experiment group assignment")
    os = Column(String, nullable=False, doc="User operating system")
    source = Column(String, nullable=False, doc="User acquisition source")

    # Relationships
    feed_actions = relationship("Feed", back_populates="user")

    # Indexes for common queries
    __table_args__ = (
        Index('idx_user_country', 'country'),
        Index('idx_user_age', 'age'),
        Index('idx_user_exp_group', 'exp_group'),
    )


class Feed(Base):
    """Feed action model representing user interactions with posts"""
    __tablename__ = 'feed_action'

    user_id = Column(Integer, ForeignKey('user.id'),
                     primary_key=True, doc="User identifier")
    post_id = Column(Integer, ForeignKey('post.id'),
                     primary_key=True, doc="Post identifier")
    action = Column(String, primary_key=True,
                    doc="Action type (like, view, etc.)")
    time = Column(DateTime, primary_key=True, doc="Action timestamp")

    # Relationships
    user = relationship("User", back_populates="feed_actions")
    post = relationship("Post", back_populates="feed_actions")

    # Indexes for common queries
    __table_args__ = (
        Index('idx_feed_user_action', 'user_id', 'action'),
        Index('idx_feed_post_action', 'post_id', 'action'),
        Index('idx_feed_time', 'time'),
        Index('idx_feed_user_time', 'user_id', 'time'),
    )
