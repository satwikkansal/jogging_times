from flask import Blueprint, request, make_response, jsonify
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_raw_jwt)
from sqlalchemy.exc import IntegrityError


from server.models import bcrypt, User, BlacklistToken, user_datastore, Role
from server.resources import api, UserList, UserDetail, RunsList, RunDetail, WeeklySummary

auth_blueprint = Blueprint('/auth', __name__)
jwt = JWTManager()


@jwt.user_claims_loader
def add_claims_to_access_token(user: User):
    return {
        'id': user.id
    }


@jwt.user_identity_loader
def user_identity_lookup(user):
    return user.id


@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    jti = decrypted_token['jti']
    return BlacklistToken.check_blacklist(jti)


@auth_blueprint.route('/login', methods=["POST"])
def login():
    post_data = request.get_json()
    user = user_datastore.find_user(id=post_data.get('user_id'))
    if user and user.verify_password(post_data.get('password')):
        access_token = create_access_token(identity=user)
        response_object = {
            'status': 'success',
            'message': 'User successfully logged in.',
            'auth_token': access_token
        }
        return make_response(jsonify(response_object)), 200
    else:
        response_object = {
            'status': 'fail',
            'message': 'User does not exist.'
        }
        return make_response(jsonify(response_object)), 404


@auth_blueprint.route('/logout', methods=["POST"])
@jwt_required
def logout():
    jti = get_raw_jwt()['jti']
    blacklist_entry = BlacklistToken(token=jti)
    try:
        blacklist_entry.save()
        return jsonify({"message": "Logged out successfully"}), 200
    except IntegrityError as e:
        return jsonify({"message": "Already logged out"}), 200


api.route(UserList, 'user_list', '/users')
api.route(UserDetail, 'user_detail', '/users/<string:id>')
api.route(RunsList, 'runs_list', '/runs')
api.route(RunDetail, 'run_detail', '/runs/<int:id>')
api.route(WeeklySummary, 'weekly_summary', '/runs/summary/')
