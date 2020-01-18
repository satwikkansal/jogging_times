from functools import wraps

from flask import abort, make_response, jsonify
from flask_jwt_extended import get_jwt_claims, verify_jwt_in_request

from server.models import User


def roles_accepted(*roles):
    """
    Verifies JWT exists, pulls out the users and checks for access restrictions based on the
    allowed roles.
    """

    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            user_id = get_jwt_claims()['id']
            user = User.query.filter_by(user_id=user_id).first()
            for role in roles:
                if user.has_role(role):
                    return fn(*args, **kwargs)
            else:
                abort(make_response(jsonify(message="User not authorized to view the list"), 403))
        return wrapper
    return decorator
