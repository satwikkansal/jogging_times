import json

from flask_testing import TestCase

from server import app, db
from server.models import Role, User


class BaseTestCase(TestCase):
    def create_app(self):
        app.config.from_object('server.config.TestingConfig')
        return app

    def setUp(self):
        self.create_app()
        db.drop_all()
        db.create_all()
        db.session.commit()
        populate_roles()
        create_admin_user()

    def tearDown(self):
        db.session.remove()

    @staticmethod
    def create_json_api_payload(resource_type, resource_id=None, attributes={}):
        """
        Generates a payload according to JSON API spec.
        """
        data = {
            "type": resource_type,
            "id": resource_id,
            "attributes": attributes
        }
        return json.dumps({
            "data": data
        })

    def assert_key_val(self, object, key, val):
        self.assertEqual(object[key], val)

    def assert_content_type_and_status(self, response, code, content_type='application/vnd.api+json'):
        self.assertStatus(response, code)
        self.assertTrue(response.content_type, content_type)

    def make_post_request(self, endpoint, data, auth_token=None):
        headers = None
        if auth_token is not None:
            headers = dict(Authorization='Bearer ' + auth_token)

        if type(data) is dict:
            data = json.dumps(data)

        response = self.client.post(
            endpoint,
            data=data,
            content_type='application/json',
            headers=headers
        )
        return response

    def make_get_request(self, endpoint, auth_token=None):
        headers = None
        if auth_token is not None:
            headers = dict(Authorization='Bearer ' + auth_token)
        response = self.client.get(
            endpoint,
            content_type='application/json',
            headers=headers
        )
        return response

    def make_delete_request(self, endpoint, auth_token=None):
        headers = None
        if auth_token is not None:
            headers = dict(Authorization='Bearer ' + auth_token)
        response = self.client.delete(
            endpoint,
            content_type='application/json',
            headers=headers
        )
        return response

    def make_patch_request(self, endpoint, data, auth_token=None):
        headers = None
        if auth_token is not None:
            headers = dict(Authorization='Bearer ' + auth_token)

        if type(data) is dict:
            data = json.dumps(data)

        response = self.client.patch(
            endpoint,
            data=data,
            content_type='application/json',
            headers=headers
        )
        return response

    def create_user(self, user_id, auth_token=None, password="random", roles=['user']):
        """
        Creates a new user.
        """
        payload = self.create_json_api_payload("user", user_id,
                                               attributes={'password': password,
                                                           "email": f"{user_id}@testmail.com",
                                                           "roles": roles})
        return self.make_post_request("/users", payload, auth_token)

    def login_user(self, user_id, password="random"):
        data = json.dumps(dict(
            user_id=user_id,
            password=password
        ))
        return self.make_post_request('/user/login', data)

    def get_login_token(self, user_id, password="random"):
        response = self.login_user(user_id, password)
        self.assertStatus(response, 200)
        return response.get_json()['auth_token']

    def log_out_user(self, auth_token):
        return self.make_post_request('/user/logout', data=None, auth_token=auth_token)


def create_admin_user():
    User(id='admin',
         password=User.get_password_hash("random"),
         email="admin@testmail.com",
         roles=[Role.query.filter_by(name="admin").first()]).save()


def populate_roles():
    Role(name="admin", description="Admin role", privileged=True).save()
    Role(name="usermanager", description="User Manager role", privileged=True).save()
    Role(name="user", description="User role").save()
