# # tests/helpers.py
# from sqlalchemy import String, Column, Float
from sqlalchemy.orm import declarative_base

# # هذا هو السطر المهم الذي كان مفقودًا
# from dev_kit.database.mixins import IDMixin, UUIDMixin, TimestampMixin, SoftDeleteMixin

# # 1. Define a single, shared Base for all test models
Base = declarative_base()


# # 2. Define all our test models in one central, importable place
# class UserModel(Base, IDMixin):
#     __tablename__ = "users_test"
#     name = Column(String)


# class ProductModel(Base, IDMixin, UUIDMixin, TimestampMixin, SoftDeleteMixin):
#     __tablename__ = "products_test"
#     name = Column(String(50), nullable=False)
#     price = Column(Float, nullable=False)
