import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pydantic import ValidationError

from app.models.models import Base, Post, User, Feed
from app.schemas.schemas import PostGet, Response


class TestDatabaseModels:
    """Test cases for database models"""

    @pytest.fixture
    def engine(self):
        """Create in-memory SQLite engine for testing"""
        return create_engine("sqlite:///:memory:")

    @pytest.fixture
    def session(self, engine):
        """Create database session"""
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        return Session()

    def test_post_model_creation(self, session):
        """Test Post model creation and retrieval"""
        # Arrange
        post = Post(
            id=1,
            text="Test post content",
            topic="Technology"
        )

        # Act
        session.add(post)
        session.commit()
        session.refresh(post)

        # Assert
        assert post.id == 1
        assert post.text == "Test post content"
        assert post.topic == "Technology"

    def test_user_model_creation(self, session):
        """Test User model creation and retrieval"""
        # Arrange
        user = User(
            id=1,
            gender=1,
            age=25,
            country="USA",
            city="New York",
            exp_group=1,
            os="iOS",
            source="organic"
        )

        # Act
        session.add(user)
        session.commit()
        session.refresh(user)

        # Assert
        assert user.id == 1
        assert user.gender == 1
        assert user.age == 25
        assert user.country == "USA"
        assert user.city == "New York"
        assert user.exp_group == 1
        assert user.os == "iOS"
        assert user.source == "organic"

    def test_feed_model_creation(self, session):
        """Test Feed model creation and retrieval"""
        # Arrange
        user = User(id=1, gender=1, age=25, country="USA",
                    city="NY", exp_group=1, os="iOS", source="organic")
        post = Post(id=1, text="Test post", topic="Tech")

        session.add(user)
        session.add(post)
        session.commit()

        feed_action = Feed(
            user_id=1,
            post_id=1,
            action="like",
            time=datetime(2024, 1, 1, 12, 0, 0)
        )

        # Act
        session.add(feed_action)
        session.commit()
        session.refresh(feed_action)

        # Assert
        assert feed_action.user_id == 1
        assert feed_action.post_id == 1
        assert feed_action.action == "like"
        assert feed_action.time == datetime(2024, 1, 1, 12, 0, 0)

    def test_feed_relationship(self, session):
        """Test Feed model relationships"""
        # Arrange
        user = User(id=1, gender=1, age=25, country="USA",
                    city="NY", exp_group=1, os="iOS", source="organic")
        post = Post(id=1, text="Test post", topic="Tech")

        session.add(user)
        session.add(post)
        session.commit()

        feed_action = Feed(
            user_id=1,
            post_id=1,
            action="like",
            time=datetime(2024, 1, 1, 12, 0, 0)
        )

        session.add(feed_action)
        session.commit()

        # Act
        retrieved_feed = session.query(Feed).filter_by(
            user_id=1, post_id=1).first()

        # Assert
        assert retrieved_feed.user.id == 1
        assert retrieved_feed.post.id == 1
        assert retrieved_feed.post.text == "Test post"

    def test_post_query_by_id(self, session):
        """Test querying posts by ID"""
        # Arrange
        posts = [
            Post(id=1, text="Post 1", topic="Technology"),
            Post(id=2, text="Post 2", topic="Science"),
            Post(id=3, text="Post 3", topic="Health")
        ]

        for post in posts:
            session.add(post)
        session.commit()

        # Act
        retrieved_posts = session.query(Post).filter(Post.id.in_([1, 3])).all()

        # Assert
        assert len(retrieved_posts) == 2
        assert retrieved_posts[0].id == 1
        assert retrieved_posts[1].id == 3

    def test_feed_query_by_user_and_action(self, session):
        """Test querying feed actions by user and action"""
        # Arrange
        user = User(id=1, gender=1, age=25, country="USA",
                    city="NY", exp_group=1, os="iOS", source="organic")
        post1 = Post(id=1, text="Post 1", topic="Tech")
        post2 = Post(id=2, text="Post 2", topic="Science")

        session.add(user)
        session.add(post1)
        session.add(post2)
        session.commit()

        feed_actions = [
            Feed(user_id=1, post_id=1, action="like",
                 time=datetime(2024, 1, 1, 12, 0, 0)),
            Feed(user_id=1, post_id=2, action="like",
                 time=datetime(2024, 1, 1, 13, 0, 0)),
            Feed(user_id=1, post_id=1, action="dislike",
                 time=datetime(2024, 1, 1, 14, 0, 0))
        ]

        for action in feed_actions:
            session.add(action)
        session.commit()

        # Act
        liked_posts = session.query(Feed.post_id).filter(
            Feed.user_id == 1,
            Feed.action == "like"
        ).distinct().all()

        # Assert
        assert len(liked_posts) == 2
        assert liked_posts[0][0] == 1
        assert liked_posts[1][0] == 2


class TestPydanticSchemas:
    """Test cases for Pydantic schemas"""

    def test_post_get_schema_valid(self):
        """Test PostGet schema with valid data"""
        # Arrange
        post_data = {
            "id": 1,
            "text": "Test post content",
            "topic": "Technology"
        }

        # Act
        post = PostGet(**post_data)

        # Assert
        assert post.id == 1
        assert post.text == "Test post content"
        assert post.topic == "Technology"

    def test_post_get_schema_invalid_id(self):
        """Test PostGet schema with invalid ID"""
        # Arrange
        post_data = {
            "id": "invalid_id",
            "text": "Test post content",
            "topic": "Technology"
        }

        # Act & Assert
        with pytest.raises(ValidationError):
            PostGet(**post_data)

    def test_post_get_schema_missing_required_field(self):
        """Test PostGet schema with missing required field"""
        # Arrange
        post_data = {
            "id": 1,
            "text": "Test post content"
            # Missing 'topic' field
        }

        # Act & Assert
        with pytest.raises(ValidationError):
            PostGet(**post_data)

    def test_post_get_schema_from_orm(self):
        """Test PostGet schema creation from ORM model"""
        # Arrange
        post = Post(
            id=1,
            text="Test post content",
            topic="Technology"
        )

        # Act
        post_get = PostGet.from_orm(post)

        # Assert
        assert post_get.id == 1
        assert post_get.text == "Test post content"
        assert post_get.topic == "Technology"

    def test_response_schema_valid(self):
        """Test Response schema with valid data"""
        # Arrange
        response_data = {
            "exp_group": "control",
            "recommendations": [
                {
                    "id": 1,
                    "text": "Post 1",
                    "topic": "Technology"
                },
                {
                    "id": 2,
                    "text": "Post 2",
                    "topic": "Science"
                }
            ]
        }

        # Act
        response = Response(**response_data)

        # Assert
        assert response.exp_group == "control"
        assert len(response.recommendations) == 2
        assert response.recommendations[0].id == 1
        assert response.recommendations[0].text == "Post 1"
        assert response.recommendations[1].id == 2
        assert response.recommendations[1].topic == "Science"

    def test_response_schema_empty_recommendations(self):
        """Test Response schema with empty recommendations"""
        # Arrange
        response_data = {
            "exp_group": "test",
            "recommendations": []
        }

        # Act
        response = Response(**response_data)

        # Assert
        assert response.exp_group == "test"
        assert len(response.recommendations) == 0

    def test_response_schema_invalid_exp_group(self):
        """Test Response schema with invalid experiment group"""
        # Arrange
        response_data = {
            "exp_group": 123,  # Should be string
            "recommendations": []
        }

        # Act & Assert
        with pytest.raises(ValidationError):
            Response(**response_data)

    def test_response_schema_invalid_recommendations(self):
        """Test Response schema with invalid recommendations"""
        # Arrange
        response_data = {
            "exp_group": "control",
            "recommendations": [
                {
                    "id": "invalid_id",  # Should be integer
                    "text": "Post 1",
                    "topic": "Technology"
                }
            ]
        }

        # Act & Assert
        with pytest.raises(ValidationError):
            Response(**response_data)

    def test_response_schema_from_orm_objects(self):
        """Test Response schema creation from ORM objects"""
        # Arrange
        posts = [
            Post(id=1, text="Post 1", topic="Technology"),
            Post(id=2, text="Post 2", topic="Science")
        ]

        # Act
        response = Response(
            exp_group="control",
            recommendations=[PostGet.from_orm(post) for post in posts]
        )

        # Assert
        assert response.exp_group == "control"
        assert len(response.recommendations) == 2
        assert response.recommendations[0].id == 1
        assert response.recommendations[1].id == 2

    def test_schema_serialization(self):
        """Test schema serialization to dict"""
        # Arrange
        post = PostGet(id=1, text="Test post", topic="Technology")
        response = Response(
            exp_group="control",
            recommendations=[post]
        )

        # Act
        post_dict = post.dict()
        response_dict = response.dict()

        # Assert
        assert post_dict["id"] == 1
        assert post_dict["text"] == "Test post"
        assert post_dict["topic"] == "Technology"

        assert response_dict["exp_group"] == "control"
        assert len(response_dict["recommendations"]) == 1
        assert response_dict["recommendations"][0]["id"] == 1
