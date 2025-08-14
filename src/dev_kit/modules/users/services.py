from datetime import datetime, timedelta
from typing import Dict, Any, Tuple

from flask_jwt_extended import create_access_token, create_refresh_token

from dev_kit.services import BaseService
from dev_kit.database.extensions import db
from dev_kit.exceptions import AuthenticationError, BusinessLogicError
from .models import User, Role, UserRoleAssociation, Permission

class UserService(BaseService[User]):
    @staticmethod
    def _validate_password_strength(password: str) -> None:
        if not password or len(password) < 8:
            raise BusinessLogicError("Password must be at least 8 characters long.")
        has_alpha = any(c.isalpha() for c in password)
        has_digit = any(c.isdigit() for c in password)
        if not (has_alpha and has_digit):
            raise BusinessLogicError("Password must include letters and numbers.")

    def _username_exists(self, username: str) -> bool:
        return (
            self._db_session.query(User).filter(User.username == username).first()
            is not None
        )
    def pre_create_hook(self, data: Dict[str, Any]) -> Dict[str, Any]:
        # Uniqueness check for username
        username = data.get("username")
        if username and self._username_exists(username):
            raise BusinessLogicError("Username already exists.")

        password = data.pop("password", None)
        if password:
            self._validate_password_strength(password)
            # Use model's helper for consistency
            temp_user = User()
            temp_user.set_password(password)
            data["password_hash"] = temp_user.password_hash
        return data

    def login_user(self, username: str, password: str) -> Tuple[User, str]:
        user = self.repo._query().filter(User.username == username).first()

        if not user or not user.check_password(password):
            raise AuthenticationError("Invalid credentials.")
        if not user.is_active:
            raise AuthenticationError("User account is not active.")
        if getattr(user, "deleted_at", None) is not None:
            raise AuthenticationError("User account has been deleted.")

        user.last_login_at = datetime.now()
        self._db_session.add(user)
        self._db_session.commit()

        roles = list(getattr(user, "roles", []))
        is_super_admin = any(getattr(role, "is_system_role", False) for role in roles)
        # Aggregate permissions from roles if available
        permissions = []
        for role in roles:
            for perm in getattr(role, "permissions", []) or []:
                name = getattr(perm, "name", None)
                if name:
                    permissions.append(name)
        # De-duplicate
        permissions = sorted(set(permissions))
        additional_claims = {
            "user_id": user.id,
            "roles": [role.name for role in roles],
            "is_super_admin": is_super_admin,
            "permissions": permissions,
        }

        access_token = create_access_token(
            identity=str(getattr(user, "uuid", user.id)),
            expires_delta=timedelta(days=1),
            additional_claims=additional_claims,
        )
        refresh_token = create_refresh_token(identity=str(getattr(user, "uuid", user.id)))
        return user, access_token, refresh_token

    def change_password(self, user_uuid: str, current_password: str, new_password: str) -> None:
        user = (
            self._db_session.query(User)
            .filter(User.uuid == user_uuid)
            .first()
        )
        if not user or not user.check_password(current_password):
            raise AuthenticationError("Invalid credentials.")
        self._validate_password_strength(new_password)
        user.set_password(new_password)
        self._db_session.add(user)
        self._db_session.commit()


user_service = UserService(model=User, db_session=db.session)


class RoleService(BaseService[Role]):
    def __init__(self):
        super().__init__(model=Role, db_session=db.session)

    def assign_role(self, user_uuid: str, role_id: int, assigned_by_user_id: int):
        # Fetch user by UUID using the shared session (Role has no UUID)
        user = (
            self._db_session.query(User)
            .filter(User.uuid == user_uuid)
            .first()
        )
        role = self._db_session.get(Role, role_id)

        if not user or not role:
            return

        existing = (
            self._db_session.query(UserRoleAssociation)
            .filter_by(user_id=user.id, role_id=role_id)
            .first()
        )
        if existing:
            return

        association = UserRoleAssociation(
            user_id=user.id, role_id=role_id, assigned_by_user_id=assigned_by_user_id
        )
        self._db_session.add(association)
        self._db_session.commit()

    def get_roles_for_user(self, user_uuid: str):
        user = (
            self._db_session.query(User)
            .filter(User.uuid == user_uuid)
            .first()
        )
        if not user:
            return []
        return user.roles

    def revoke_role(self, user_uuid: str, role_id: int):
        user = (
            self._db_session.query(User)
            .filter(User.uuid == user_uuid)
            .first()
        )
        if not user:
            return
        assoc = (
            self._db_session.query(UserRoleAssociation)
            .filter_by(user_id=user.id, role_id=role_id)
            .first()
        )
        if assoc:
            self._db_session.delete(assoc)
            self._db_session.commit()


class PermissionService(BaseService[Permission]):
    def __init__(self):
        super().__init__(model=Permission, db_session=db.session)

    def assign_permission_to_role(self, role_id: int, permission_id: int):
        role = self._db_session.get(Role, role_id)
        perm = self._db_session.get(Permission, permission_id)
        if not role or not perm:
            return
        if perm not in role.permissions:
            role.permissions.append(perm)
            self._db_session.add(role)
            self._db_session.commit()

    def revoke_permission_from_role(self, role_id: int, permission_id: int):
        role = self._db_session.get(Role, role_id)
        perm = self._db_session.get(Permission, permission_id)
        if not role or not perm:
            return
        if perm in role.permissions:
            role.permissions.remove(perm)
            self._db_session.add(role)
            self._db_session.commit()

    def list_role_permissions(self, role_id: int):
        role = self._db_session.get(Role, role_id)
        return [] if not role else role.permissions


role_service = RoleService()
permission_service = PermissionService()
