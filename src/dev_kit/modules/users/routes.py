from apiflask import APIBlueprint
from flask import jsonify, make_response
from flask_jwt_extended import (
    set_access_cookies,
    set_refresh_cookies,
    unset_jwt_cookies,
    jwt_required,
    get_jwt_identity,
)

from dev_kit.web.routing import register_crud_routes
from dev_kit.web.schemas import MessageSchema
from dev_kit.web.decorators import permission_required
from dev_kit.exceptions import AuthenticationError
from .schemas import (
    user_schemas,
    LoginSchema,
    AuthTokenSchema,
    role_schemas,
    AssignRoleSchema,
    permission_schemas,
    ChangePasswordSchema,
    PermissionIdSchema,
)
from .services import user_service, role_service, permission_service

# إنشاء Blueprint خاص بالوحدة
auth_bp = APIBlueprint("auth", __name__, url_prefix="/auth")
users_bp = APIBlueprint("users", __name__, url_prefix="/users")
roles_bp = APIBlueprint("roles", __name__, url_prefix="/roles")
permissions_bp = APIBlueprint("permissions", __name__, url_prefix="/permissions")

# تسجيل مسارات CRUD تلقائياً لهذه الوحدة
register_crud_routes(
    bp=users_bp,
    service=user_service,
    schemas=user_schemas,
    entity_name="user",
    id_field="uuid",
)
register_crud_routes(
    bp=roles_bp,
    service=role_service,
    schemas=role_schemas,
    entity_name="role",
    id_field="id",
)

register_crud_routes(
    bp=permissions_bp,
    service=permission_service,
    schemas=permission_schemas,
    entity_name="permission",
    id_field="id",
)

@roles_bp.post("/users/<string:user_uuid>")
@roles_bp.input(AssignRoleSchema)
@roles_bp.output(MessageSchema)
@roles_bp.doc(summary="Assign Role To User")
@jwt_required()
@permission_required("assign_role:user")
def assign_role(user_uuid, json_data):
    role_id = json_data["role_id"]
    from flask_jwt_extended import get_jwt

    claims = get_jwt()
    current_user_id = claims.get("user_id")
    role_service.assign_role(
        user_uuid=user_uuid, role_id=role_id, assigned_by_user_id=current_user_id
    )
    return {"message": "Role assigned successfully"}

@roles_bp.get("/users/<string:user_uuid>")
@roles_bp.output(role_schemas["main"](many=True))
@roles_bp.doc(summary="List Roles Assigned To User")
@jwt_required()
@permission_required("read_roles:user")
def list_user_roles(user_uuid):
    return role_service.get_roles_for_user(user_uuid)


@auth_bp.post("/login")
@auth_bp.input(LoginSchema)
@auth_bp.output(AuthTokenSchema)
@auth_bp.doc(summary="User Login")
def login(json_data):
    user, access_token, refresh_token = user_service.login_user(
        username=json_data["username"], password=json_data["password"]
    )
    user_data = user_schemas["main"]().dump(user)
    resp = make_response(
        jsonify({"user": user_data, "access_token": access_token, "refresh_token": refresh_token})
    )
    set_access_cookies(resp, access_token)
    set_refresh_cookies(resp, refresh_token)
    return resp


@auth_bp.get("/me")
@jwt_required()
@auth_bp.output(user_schemas["main"])
@auth_bp.doc(summary="Current Authenticated User")
def whoami():
    user_uuid = get_jwt_identity()
    user = user_service.get_by_uuid(user_uuid) if hasattr(user_service, "get_by_uuid") else None
    if user is None:
        from .models import User
        user = db.session.query(User).filter(User.uuid == user_uuid).first()
    return user


@auth_bp.post("/refresh")
@jwt_required(refresh=True)
@auth_bp.output(AuthTokenSchema)
@auth_bp.doc(summary="Refresh Access Token")
def refresh():
    user_uuid = get_jwt_identity()
    from flask_jwt_extended import create_access_token
    new_access = create_access_token(identity=user_uuid)
    resp = make_response(jsonify({"access_token": new_access, "refresh_token": None, "user": None}))
    set_access_cookies(resp, new_access)
    return resp


@auth_bp.post("/logout")
@jwt_required(optional=True)
@auth_bp.output(MessageSchema)
@auth_bp.doc(summary="Logout and clear tokens")
def logout():
    resp = make_response(jsonify({"message": "Logged out"}))
    unset_jwt_cookies(resp)
    return resp


@roles_bp.delete("/users/<string:user_uuid>")
@roles_bp.input(AssignRoleSchema)
@roles_bp.output(MessageSchema)
@roles_bp.doc(summary="Revoke Role From User")
@jwt_required()
@permission_required("revoke_role:user")
def revoke_role(user_uuid, json_data):
    role_id = json_data["role_id"]
    role_service.revoke_role(user_uuid=user_uuid, role_id=role_id)
    return {"message": "Role revoked successfully"}


@roles_bp.get("/<int:role_id>/permissions")
@roles_bp.output(permission_schemas["main"](many=True))
@roles_bp.doc(summary="List Permissions For Role")
@jwt_required()
@permission_required("read_permissions:role")
def list_role_permissions(role_id: int):
    return permission_service.list_role_permissions(role_id)


@roles_bp.post("/<int:role_id>/permissions")
@roles_bp.input(PermissionIdSchema)
@roles_bp.output(MessageSchema)
@roles_bp.doc(summary="Assign Permission To Role")
@jwt_required()
@permission_required("assign_permission:role")
def assign_permission(role_id: int, json_data):
    permission_service.assign_permission_to_role(role_id, json_data["permission_id"])
    return {"message": "Permission assigned to role"}


@roles_bp.delete("/<int:role_id>/permissions")
@roles_bp.input(PermissionIdSchema)
@roles_bp.output(MessageSchema)
@roles_bp.doc(summary="Revoke Permission From Role")
@jwt_required()
@permission_required("revoke_permission:role")
def revoke_permission(role_id: int, json_data):
    permission_service.revoke_permission_from_role(role_id, json_data["permission_id"])
    return {"message": "Permission revoked from role"}


@users_bp.post("/change-password")
@users_bp.input(ChangePasswordSchema)
@users_bp.output(MessageSchema)
@users_bp.doc(summary="Change current user's password")
@jwt_required()
def change_password(json_data):
    user_uuid = get_jwt_identity()
    user_service.change_password(
        user_uuid=user_uuid,
        current_password=json_data["current_password"],
        new_password=json_data["new_password"],
    )
    return {"message": "Password changed successfully"}
