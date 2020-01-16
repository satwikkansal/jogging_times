import os

from flask import Blueprint, request, make_response, jsonify, abort
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_raw_jwt)
from sqlalchemy.exc import IntegrityError


from server.models import bcrypt, User, BlacklistToken, user_datastore, Role
from server.utils.decorators import roles_accepted

user_blueprint = Blueprint('users', __name__)
jwt = JWTManager()


@jwt.user_claims_loader
def add_claims_to_access_token(user: User):
    return {
        'id': user.username
    }


@jwt.user_identity_loader
def user_identity_lookup(user):
    return user.username


@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    jti = decrypted_token['jti']
    BlacklistToken.check_blacklist(jti)


@user_blueprint.route('/new', methods=["POST"])
def create_user():
    # get the post data
    post_data = request.get_json()
    username = post_data.get('username'),
    password = post_data.get('password')
    email = post_data.get('email')
    roles = post_data.get('roles', ["user"])
    # check if user already exists
    user = User.query.filter_by(username=username).first()
    if not user:
        password = bcrypt.generate_password_hash(
            password, os.getenv('BCRYPT_LOG_ROUNDS')).decode('utf-8')

        role_objects = []
        for role in roles:
            role_objects.append(Role.query.filter_by(name=role).first())

        user = User(username=username, password=password, email=email, roles=role_objects)

        user.save()

        # generate the auth token
        access_token = create_access_token(identity=user)

        response_object = {
            'status': 'success',
            'message': 'User successfully registered.',
            'auth_token': access_token
        }
        return make_response(jsonify(response_object)), 201
    else:
        response_object = {
            'status': 'fail',
            'message': 'User already exists. Please log in.',
        }
        return make_response(jsonify(response_object)), 202


@user_blueprint.route('/login', methods=["POST"])
def login():
    # get the post data
    post_data = request.get_json()
    # fetch the user data
    user = user_datastore.find_user(username=post_data.get('username'))
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


@user_blueprint.route('/logout', methods=["POST"])
@jwt_required
def logout():
    jti = get_raw_jwt()['jti']
    blacklist_entry = BlacklistToken(token=jti)
    try:
        blacklist_entry.save()
        return jsonify({"msg": "Logged out successfully"}), 200
    except IntegrityError as e:
        return jsonify({"msg": "Already logged out"}), 200


@user_blueprint.route('/list', methods=["POST"])
@roles_accepted('admin', 'usermanager')
def get_user_list():
    return "Here's your user list", 200
