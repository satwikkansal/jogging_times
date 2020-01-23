from tests.base import BaseTestCase


class TestAuthBlueprint(BaseTestCase):
    def test_list_users_user_role(self):
        # A user should be able to see itself
        self.create_user("user1")
        self.create_user("user2")

        user1_token = self.get_login_token("user1")
        response = self.make_get_request('/users', user1_token)
        self.assert_content_type_and_status(response, 200)
        response_json = response.get_json()
        meta = response_json['meta']
        self.assertEqual(1, meta['count'])
        data = response_json['data']
        self.assertEqual("user1", data[0]["id"])

    def test_list_users_privileged_role(self):
        # A privileged user can see all the other users.
        self.create_user("user1")
        self.create_user("user2")

        admin_token = self.get_login_token("admin")

        self.create_user("user_manger", admin_token, roles=["usermanager"])

        response = self.make_get_request('/users', admin_token)
        self.assert_content_type_and_status(response, 200)
        response_json = response.get_json()
        meta = response_json['meta']
        # 2 users, 1 user-manager, and 1 admin itself.
        self.assertEqual(4, meta['count'])

    def test_delete_users_user_role(self):
        # A user should be able to delete only itself.
        self.create_user("user1")
        self.create_user("user2")
        self.create_user("user3")

        user1_token = self.get_login_token("user1")
        response = self.make_delete_request("/users/user1", user1_token)
        self.assert_content_type_and_status(response, 200)

        # user 1 trying to delete itself again
        response = self.make_delete_request("/users/user1", user1_token)
        self.assert_content_type_and_status(response, 403)
        self.assertIn(b"Unable to fetch existing user", response.data)

        user2_token = self.get_login_token("user2")
        # user 2 trying to delete user 3
        response = self.make_delete_request("/users/user3", user2_token)
        self.assert_content_type_and_status(response, 403)
        self.assertIn(b"User doesn\'t have permission to access", response.data)

    def test_delete_users_privileged_role(self):
        self.create_user("user1")
        self.create_user("user2")

        admin_token = self.get_login_token("admin")
        self.create_user("user_manager", admin_token, roles=["usermanager"])
        user_manager_token = self.get_login_token("user_manager")

        response = self.make_delete_request("/users/user1", user_manager_token)
        self.assert_content_type_and_status(response, 200)

        # user manager trying to delete user1 again
        response = self.make_delete_request("/users/user1", user_manager_token)
        self.assert_content_type_and_status(response, 404)
        self.assertIn(b"user1 not found", response.data)

        # user manager trying to delete admin
        response = self.make_delete_request("/users/admin", user_manager_token)
        self.assert_content_type_and_status(response, 403)
        self.assertIn(b"User doesn\'t have permission to access", response.data)

        # user manager trying to delete itself
        response = self.make_delete_request("/users/user_manager", user_manager_token)
        self.assert_content_type_and_status(response, 200)

        self.create_user("user_manager", admin_token, roles=["usermanager"])

        # Admin trying to delete user manager
        response = self.make_delete_request("/users/user_manager", admin_token)
        self.assert_content_type_and_status(response, 200)

        response = self.make_delete_request("/users/user2", admin_token)
        self.assert_content_type_and_status(response, 200)

        # Make sure the count is 1 now
        response = self.make_get_request('/users', admin_token)
        self.assert_content_type_and_status(response, 200)
        response_json = response.get_json()
        meta = response_json['meta']
        # Admin itself
        self.assertEqual(1, meta['count'])
        data = response_json['data']
        self.assertEqual("admin", data[0]["id"])

    def test_update_users_user_role(self):
        # A user should be able to update only itself.
        self.create_user("user1")
        self.create_user("user2")
        self.create_user("user3")

        user1_token = self.get_login_token("user1")
        first_name = "Some first name"

        patch_data = {
            "data":  {
                "type": "user",
                "id": "user1",
                "attributes": {
                    "first_name": first_name
                }
            }
        }

        response = self.make_patch_request("/users/user1", patch_data, user1_token)
        self.assert_content_type_and_status(response, 200)
        data = response.get_json()['data']
        self.assertEqual(first_name, data['attributes']['first_name'])

        # user 1 trying to update itself again
        response = self.make_patch_request("/users/user1", patch_data, user1_token)
        self.assert_content_type_and_status(response, 200)

        user2_token = self.get_login_token("user2")
        # user 2 trying to update user 3
        patch_data['data']['id'] = 'user3'
        response = self.make_patch_request("/users/user3", patch_data, user2_token)
        self.assert_content_type_and_status(response, 403)
        self.assertIn(b"User doesn\'t have permission to access", response.data)

    def test_patch_users_privileged_role(self):
        self.create_user("user1")
        self.create_user("user2")

        admin_token = self.get_login_token("admin")
        self.create_user("user_manager", admin_token, roles=["usermanager"])
        user_manager_token = self.get_login_token("user_manager")
        first_name = "Some first name"

        patch_data = {
            "data": {
                "type": "user",
                "id": "user1",
                "attributes": {
                    "first_name": first_name
                }
            }
        }

        response = self.make_patch_request("/users/user1", patch_data, user_manager_token)
        self.assert_content_type_and_status(response, 200)

        # user manager trying to update admin
        patch_data['data']['id'] = 'admin'
        response = self.make_patch_request("/users/admin", patch_data, user_manager_token)
        self.assert_content_type_and_status(response, 403)
        self.assertIn(b"User doesn\'t have permission to access", response.data)

        # user manager trying to update itself
        patch_data['data']['id'] = 'user_manager'
        response = self.make_patch_request("/users/user_manager", patch_data, user_manager_token)
        self.assert_content_type_and_status(response, 200)

        self.create_user("user_manager_2", admin_token, roles=["usermanager"])

        # User manager trying to update another user manager
        patch_data['data']['id'] = 'user_manager_2'
        response = self.make_patch_request("/users/user_manager_2", patch_data, user_manager_token)
        self.assert_content_type_and_status(response, 403)

        # Admin trying to update user manager
        response = self.make_patch_request("/users/user_manager_2", patch_data, admin_token)
        self.assert_content_type_and_status(response, 200)
