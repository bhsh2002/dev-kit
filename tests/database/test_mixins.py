# tests/database/test_mixins.py

from sqlalchemy import create_engine, String, Column
from sqlalchemy.orm import sessionmaker, declarative_base

from dev_kit.database.mixins import IDMixin, UUIDMixin, TimestampMixin, SoftDeleteMixin

# --- Test Setup ---
# 1. Create an in-memory SQLite database for testing
engine = create_engine("sqlite:///:memory:")
Session = sessionmaker(bind=engine)
Base = declarative_base()


# 2. Create a temporary test model that uses all our mixins
class SampleEntity(Base, IDMixin, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "sample_entities"
    name = Column(String, default="test")


# 3. Create the table in the in-memory database
Base.metadata.create_all(engine)
# --- End Test Setup ---


def test_mixins_populate_fields_on_create():
    """
    Tests if all mixins correctly populate their respective fields
    when a new entity is created.
    """
    # Arrange: Create a new session
    session = Session()

    # Action: Create an instance of our test entity and save it
    new_entity = SampleEntity()
    session.add(new_entity)
    session.commit()
    session.refresh(new_entity)

    # Assert: Check that all mixin-provided fields have values
    assert new_entity.id is not None
    assert isinstance(new_entity.id, int)

    assert new_entity.uuid is not None
    assert isinstance(new_entity.uuid, str)
    assert len(new_entity.uuid) == 36  # Standard UUID4 length

    assert new_entity.created_at is not None
    assert new_entity.updated_at is not None

    # The soft delete field should be None on creation
    assert new_entity.deleted_at is None

    # Clean up the session
    session.close()
