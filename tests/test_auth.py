import time
import unittest
import datetime

from tests.base import BaseTestCase


class TestAuthBlueprint(BaseTestCase):

    def test_registration(self):
        user_id = "joe"
        password = "hello123"
        admin_token = self.get_login_token("admin")
        response = self.create_user(user_id, admin_token, password)
        self.assert_content_type_and_status(response, 201)
        data = response.get_json()['data']
        self.assert_key_val(data, 'type', 'user')
        self.assert_key_val(data, 'id', user_id)
        attributes = data['attributes']
        self.assert_key_val(attributes, 'email', f'{user_id}@testmail.com')
        self.assert_key_val(attributes, 'roles', ['user'])

    def test_registration_multiple_roles(self):
        user_id = "joe"
        user_roles = ['admin', 'usermanager', 'user']
        admin_token = self.get_login_token("admin")
        response = self.create_user(user_id, admin_token, roles=user_roles)
        self.assert_content_type_and_status(response, 201)
        data = response.get_json()['data']
        self.assert_key_val(data, 'type', 'user')
        self.assert_key_val(data, 'id', user_id)
        attributes = data['attributes']
        self.assert_key_val(attributes, 'email', f'{user_id}@testmail.com')
        self.assert_key_val(attributes, 'roles', user_roles)

    def test_registered_with_already_registered_user(self):
        user_id = "joe"
        admin_token = self.get_login_token("admin")
        response = self.create_user(user_id, admin_token)
        self.assert_content_type_and_status(response, 201)
        response = self.create_user(user_id, admin_token)
        self.assert_content_type_and_status(response, 409)

    def test_login(self):
        user_id = "joe"
        admin_token = self.get_login_token("admin")
        self.create_user(user_id, admin_token)
        response = self.login_user(user_id)
        self.assertStatus(response, 200)

    def test_logout(self):
        user_id = "joe"
        admin_token = self.get_login_token("admin")
        self.create_user(user_id, admin_token)
        auth_token = self.get_login_token(user_id)
        response = self.log_out_user(auth_token)
        self.assertStatus(response, 200)
        message = response.get_json()['message']
        self.assertEqual(message, "Logged out successfully")

    def test_logout_blacklisted_token(self):
        user_id = "joe"
        admin_token = self.get_login_token("admin")
        self.create_user(user_id, admin_token)
        auth_token = self.get_login_token(user_id)
        response = self.log_out_user(auth_token)
        self.assertStatus(response, 200)
        response = self.log_out_user(auth_token)
        self.assertStatus(response, 401)
        message = response.get_json()['message']
        self.assertEqual(message, "Token has been revoked")

    def test_non_registered_user_login(self):
        user_id = "joe"
        response = self.login_user(user_id)
        self.assertStatus(response, 404)
        message = response.get_json()['message']
        self.assertEqual(message, "User does not exist.")

    def test_logout_malformed_bearer_token(self):
        user_id = "joe"
        admin_token = self.get_login_token("admin")
        self.create_user(user_id, admin_token)
        auth_token = self.get_login_token(user_id)
        response = self.log_out_user(auth_token + "garbage string")
        self.assertStatus(response, 422)
        message = response.get_json()['message']
        self.assertIn("Bad Authorization header", message)

    def test_logout_with_expired_token(self):
        self.app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(microseconds=500)
        user_id = "joe"
        admin_token = self.get_login_token("admin")
        self.create_user(user_id, admin_token)
        auth_token = self.get_login_token(user_id)
        time.sleep(1)
        response = self.log_out_user(auth_token)
        self.assertStatus(response, 401)
        message = response.get_json()['message']
        self.assertEqual(message, "Token has expired")
        self.app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(minutes=15)


if __name__ == '__main__':
    unittest.main()
