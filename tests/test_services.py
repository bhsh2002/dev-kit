# # tests/test_services.py
# import pytest
# from unittest.mock import patch
# from tests.helpers import UserModel
# from dev_kit.exceptions import NotFoundError, DatabaseError


# def test_create_commits_data(db_session, user_service):
#     """Tests that the create method persists data."""
#     created_user = user_service.create({"name": "Bahaa"})
#     assert created_user.id is not None

#     # Verify that the data is in the database by querying it
#     fetched_user = db_session.query(UserModel).filter_by(id=created_user.id).one()
#     assert fetched_user.name == "Bahaa"


# def test_update_not_found_raises_error(user_service):
#     """Tests that updating a non-existent entity raises an error."""
#     with pytest.raises(NotFoundError):
#         user_service.update(entity_id=999, data={"name": "Ghost"})


# def test_handle_session_rolls_back_on_error(db_session, user_service):
#     """Tests that the decorator rolls back changes on a failed operation."""
#     # Arrange: Create a user and flush it to the DB within the test's transaction
#     initial_user = UserModel(name="Initial Name")
#     db_session.add(initial_user)
#     db_session.flush()
#     user_id = initial_user.id

#     # Action: Mock a repository method to simulate a failure during the update.
#     with patch.object(
#         user_service.repo, "get_by_id", side_effect=DatabaseError("Simulated DB Error")
#     ):
#         with pytest.raises(DatabaseError):
#             # This update call will fail, and the decorator should rollback.
#             user_service.update(entity_id=user_id, data={"name": "Changed Name"})

#     # Assert: The user should still exist, and their name should NOT have changed.
#     # The main test transaction (from the fixture)
#     #  has not been committed or rolled back yet.
#     user_after_failed_update = db_session.query(UserModel).filter_by(id=user_id).one()
#     assert user_after_failed_update.name == "Initial Name"
