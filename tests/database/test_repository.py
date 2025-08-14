# # tests/database/test_repository.py

# # The test functions only need the product_repo and db_session fixtures,
# # which are provided automatically from conftest.py
# def test_create_and_get(db_session, product_repo):
#     product_data = {"name": "Laptop", "price": 1500.0}
#     created_product = product_repo.create(product_data)
#     db_session.commit()  # Commit is needed as repo doesn't auto-commit

#     assert created_product.id is not None
#     retrieved_product = product_repo.get_by_id(created_product.id)
#     assert retrieved_product.id == created_product.id


# def test_soft_delete_logic(db_session, product_repo):
#     product = product_repo.create({"name": "Mouse", "price": 50.0})
#     db_session.commit()
#     product_id = product.id

#     product_repo.delete(product, soft=True)
#     db_session.commit()

#     assert product_repo.get_by_id(product_id) is None
#     assert product_repo.get_by_id(product_id, include_soft_deleted=True) is not None


# def test_pagination(db_session, product_repo):
#     for i in range(25):
#         product_repo.create({"name": f"Item {i}", "price": 10.0 + i})
#     db_session.commit()

#     result = product_repo.paginate(page=2, per_page=10)

#     assert result.total == 25
#     assert len(result.items) == 10
#     assert result.has_next is True
