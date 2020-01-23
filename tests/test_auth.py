import time
import unittest
import datetime

from tests.base import BaseTestCase


class TestAuthBlueprint(BaseTestCase):

    def test_registration(self):
        user_id = "joe"
        password = "hello123"
        response = self.create_user(user_id, password=password)
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

    def test_registration_privileged_roles_without_auth(self):
        user_id = "joe"
        user_roles = ['admin', 'usermanager', 'user']
        response = self.create_user(user_id, roles=user_roles)
        self.assert_content_type_and_status(response, 401)
        message = response.get_json()['message']
        self.assertEqual(message, "Missing Authorization Header")

    def test_registration_privileged_roles_with_non_privileged_auth(self):
        user_id = "some_user"
        user_roles = ['user']
        response = self.create_user(user_id, roles=user_roles)
        self.assert_content_type_and_status(response, 201)

        # User trying to create a usermanager
        user_auth = self.get_login_token(user_id)
        user_manager = "user_manager"
        user_roles = ["usermanager"]
        response = self.create_user(user_manager, auth_token=user_auth, roles=user_roles)
        self.assert_content_type_and_status(response, 403)

        # User manager trying to create another usermanager / admin
        admin_token = self.get_login_token("admin")
        response = self.create_user(user_manager, admin_token, roles=user_roles)
        self.assert_content_type_and_status(response, 201)
        user_manager_token = self.get_login_token(user_manager)
        another_admin = "another_admin"
        another_admin_roles = ["admin", "usermanager"]
        response = self.create_user(another_admin, auth_token=user_manager_token, roles=another_admin_roles)
        self.assert_content_type_and_status(response, 403)

    def test_registered_with_already_registered_user(self):
        user_id = "joe"
        response = self.create_user(user_id)
        self.assert_content_type_and_status(response, 201)
        response = self.create_user(user_id)
        self.assert_content_type_and_status(response, 409)

    def test_login(self):
        user_id = "joe"
        self.create_user(user_id)
        response = self.login_user(user_id)
        self.assertStatus(response, 200)

    def test_logout(self):
        user_id = "joe"
        self.create_user(user_id)
        auth_token = self.get_login_token(user_id)
        response = self.log_out_user(auth_token)
        self.assertStatus(response, 200)
        message = response.get_json()['message']
        self.assertEqual(message, "Logged out successfully")

    def test_logout_blacklisted_token(self):
        user_id = "joe"
        self.create_user(user_id)
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
        self.create_user(user_id)
        auth_token = self.get_login_token(user_id)
        response = self.log_out_user(auth_token + "garbage string")
        self.assertStatus(response, 422)
        message = response.get_json()['message']
        self.assertIn("Bad Authorization header", message)

    def test_logout_with_expired_token(self):
        self.app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(microseconds=500)
        user_id = "joe"
        self.create_user(user_id)
        auth_token = self.get_login_token(user_id)
        time.sleep(1)
        response = self.log_out_user(auth_token)
        self.assertStatus(response, 401)
        message = response.get_json()['message']
        self.assertEqual(message, "Token has expired")
        self.app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(minutes=15)



if __name__ == '__main__':
    unittest.main()
