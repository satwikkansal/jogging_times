from functools import wraps

from flask import abort, make_response, jsonify, request
from flask_jwt_extended import get_jwt_claims, verify_jwt_in_request
from flask_rest_jsonapi import JsonApiException

from server.models import User


def verify_roles(user, allowed_roles):
    for role in allowed_roles:
        if user.has_role(role):
            return True


def raise_permission_denied_exception(reason):
    raise JsonApiException(
        reason,
        "Permission check",
        title='Permission denied',
        status='403')


def get_user_from_jwt():
    verify_jwt_in_request()
    try:
        user_id = get_jwt_claims()['id']
        user = User.query.filter_by(id=user_id).first()
        if not user:
            raise Exception
        return user
    except Exception as e:
        print(e)
        raise_permission_denied_exception("Unable to fetch existing user from JWT")


def roles_accepted(*roles, role_validator=None):
    """
    Verifies JWT exists, pulls out the users and checks for access restrictions based on the
    allowed roles.
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            user = get_user_from_jwt()
            for role in roles:
                if user.has_role(role) and role_validator(user.roles, ["user"]):
                    return fn(*args, **kwargs)
            else:
                abort(make_response(jsonify(message="User not authorized for this resource"), 403))
        return wrapper
    return decorator
