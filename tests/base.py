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

    def create_user(self, user_id, auth_token, password="random", roles=['user']):
        """
        Creates a new user.
        """
        payload = self.create_json_api_payload("user", user_id,
                                               attributes={'password': password,
                                                           "email": f"{user_id}@testmail.com",
                                                           "roles": roles})
        response = self.client.post(
            '/users',
            data=payload,
            content_type='application/json',
            headers=dict(Authorization='Bearer ' + auth_token)
        )
        return response

    def login_user(self, user_id, password="random"):
        return self.client.post(
            '/user/login',
            data=json.dumps(dict(
                user_id=user_id,
                password=password
            )),
            content_type='application/json',
        )

    def get_login_token(self, user_id, password="random"):
        response = self.login_user(user_id, password)
        self.assertStatus(response, 200)
        return response.get_json()['auth_token']


def create_admin_user():
    User(id='admin',
         password=User.get_password_hash("random"),
         email="admin@testmail.com",
         roles=[Role.query.filter_by(name="admin").first()]).save()


def populate_roles():
    Role(name="admin", description="Admin role").save()
    Role(name="usermanager", description="User Manager role").save()
    Role(name="user", description="User role").save()

