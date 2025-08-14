from sqlalchemy import String, Column, VARCHAR, BOOLEAN, TIMESTAMP, INTEGER, Table, ForeignKey, TEXT
from sqlalchemy import func, text
from sqlalchemy.orm import declarative_base, relationship
from werkzeug.security import generate_password_hash, check_password_hash

from dev_kit.database.mixins import IDMixin, TimestampMixin, UUIDMixin, SoftDeleteMixin

Base = declarative_base()


class User(Base, IDMixin, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "users"
    username = Column(String(80), unique=True, nullable=False)
    password_hash = Column(VARCHAR(255), nullable=False)
    is_active = Column(BOOLEAN, nullable=False, default=True)
    last_login_at = Column(TIMESTAMP, nullable=True)

    # Relationships to roles (defined below)
    assigned_roles_details = relationship(
        "UserRoleAssociation",
        foreign_keys="UserRoleAssociation.user_id",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    roles_assigned_by_me = relationship(
        "UserRoleAssociation",
        foreign_keys="UserRoleAssociation.assigned_by_user_id",
        back_populates="assigner",
    )
    roles = relationship(
        "Role",
        secondary="user_roles",
        primaryjoin="User.id == UserRoleAssociation.user_id",
        secondaryjoin="Role.id == UserRoleAssociation.role_id",
        viewonly=True,
    )

    def set_password(self, password):
        if not password:
            raise ValueError("Password cannot be empty.")
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        if not self.password_hash or not password:
            return False
        return check_password_hash(self.password_hash, password)


# Association table and role/permission models (lightweight, optional use)

class Role(Base, IDMixin, TimestampMixin):
    __tablename__ = "roles"
    name = Column(VARCHAR(50), unique=True, nullable=False)
    display_name = Column(VARCHAR(50), nullable=False)
    description = Column(TEXT, nullable=True)
    is_system_role = Column(BOOLEAN, nullable=False, default=False)

    user_associations = relationship(
        "UserRoleAssociation",
        foreign_keys="UserRoleAssociation.role_id",
        back_populates="role",
        cascade="all, delete-orphan",
    )
    users = relationship(
        "User",
        secondary="user_roles",
        primaryjoin="Role.id == UserRoleAssociation.role_id",
        secondaryjoin="User.id == UserRoleAssociation.user_id",
        viewonly=True,
    )


class UserRoleAssociation(Base):
    __tablename__ = "user_roles"

    user_id = Column(INTEGER, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    role_id = Column(INTEGER, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True)
    assigned_at = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    assigned_by_user_id = Column(
        INTEGER, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )

    user = relationship("User", foreign_keys=[user_id], back_populates="assigned_roles_details")
    role = relationship("Role", foreign_keys=[role_id], back_populates="user_associations")
    assigner = relationship("User", foreign_keys=[assigned_by_user_id], back_populates="roles_assigned_by_me")


class Permission(Base, IDMixin, TimestampMixin):
    __tablename__ = "permissions"
    name = Column(VARCHAR(100), unique=True, nullable=False)  # e.g., "create:user"
    description = Column(TEXT, nullable=True)

    # Many-to-many with roles via association table
    role_permissions = Table(
        "role_permissions",
        Base.metadata,
        Column("role_id", INTEGER, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
        Column(
            "permission_id",
            INTEGER,
            ForeignKey("permissions.id", ondelete="CASCADE"),
            primary_key=True,
        ),
    )

    roles = relationship("Role", secondary=role_permissions, backref="permissions")
