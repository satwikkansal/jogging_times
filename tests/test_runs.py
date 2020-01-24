import json
from copy import deepcopy

from tests.base import BaseTestCase

sample_run_object = {
            "data": {
                "type": "run",
                "attributes": {
                    "start_time": "2020-01-20T16:34:34.838199",
                    "end_time": "2020-01-20T16:54:45.838199",
                    "start_lat": "12.8947909",
                    "start_lng": "77.6427151",
                    "end_lat": "12.8986343",
                    "end_lng": "77.656089",
                    "distance": "3100"
                },
                "relationships": {
                    "user": {
                        "data": {
                            "type": "user",
                            "id": "user1"
                        }
                    }
                }
            }
        }


class TestRunsEndpoint(BaseTestCase):

    def test_create_new_run(self):
        user_id = "user1"
        self.create_user(user_id)
        run_object = deepcopy(sample_run_object)
        user_token = self.get_login_token(user_id)

        # Without user token
        response = self.make_post_request("/runs", run_object)
        self.assert_content_type_and_status(response, 401)
        message = response.get_json()['message']
        self.assertEqual(message, "Missing Authorization Header")

        response = self.make_post_request("/runs", run_object, user_token)
        self.assert_content_type_and_status(response, 201)

        json_response = response.get_json()
        # Check if weather info is present
        data = json_response['data']
        self.assertIsNotNone(json.loads(data['attributes'].get('weather_info')))
        # Check if relationships info is present
        self.assertEqual('/users/user1', data['relationships']['user']['links']['related'])

        # Without relationships
        del run_object['data']['relationships']
        response = self.make_post_request("/runs", run_object, user_token)
        self.assert_content_type_and_status(response, 403)
        self.assertIn(b'Please provide a User relationship for the Run', response.data)

    def test_create_new_run_user_mismatch(self):
        user_id = "user1"
        self.create_user(user_id)
        self.create_user("user2")
        run_object = deepcopy(sample_run_object)
        user_1_token = self.get_login_token(user_id)

        run_object['data']['relationships']['user']['data']['id'] = 'user2'
        response = self.make_post_request("/runs", run_object, user_1_token)
        self.assert_content_type_and_status(response, 403)
        self.assertIn(b"User doesn't have permission to create Run for another user", response.data)

    def test_create_new_run_by_admin(self):
        user_id = "user1"
        self.create_user(user_id)
        run_object = deepcopy(sample_run_object)
        admin_token = self.get_login_token("admin")

        response = self.make_post_request("/runs", run_object, admin_token)
        self.assert_content_type_and_status(response, 201)

        # Admin creating Run for a user that's non existent
        run_object['data']['relationships']['user']['data']['id'] = 'user2'
        response = self.make_post_request("/runs", run_object, admin_token)
        self.assert_content_type_and_status(response, 404)
        self.assertIn(b"user2 not found", response.data)

    def test_list_runs(self):
        user1_id = "user1"
        user2_id = "user2"
        self.create_user(user1_id)
        self.create_user(user2_id)
        run_object = deepcopy(sample_run_object)
        user1_token = self.get_login_token(user1_id)

        # Run 1 for user1
        response = self.make_post_request("/runs", run_object, user1_token)
        self.assert_content_type_and_status(response, 201)

        # Run 2 for user1
        response = self.make_post_request("/runs", run_object, user1_token)
        self.assert_content_type_and_status(response, 201)

        run_object['data']['relationships']['user']['data']['id'] = user2_id
        user2_token = self.get_login_token(user2_id)
        # Run 1 for user2
        response = self.make_post_request("/runs", run_object, user2_token)

        # Without user token
        response = self.make_get_request("/runs")
        self.assert_content_type_and_status(response, 401)

        # List for user 1
        response = self.make_get_request("/runs", user1_token)
        self.assert_content_type_and_status(response, 200)
        json_response = response.get_json()
        self.assertEqual(2, json_response['meta']['count'])

        # List for user 2
        response = self.make_get_request("/runs", user2_token)
        self.assert_content_type_and_status(response, 200)
        json_response = response.get_json()
        self.assertEqual(1, json_response['meta']['count'])

        # List for admin
        admin_token = self.get_login_token("admin")
        response = self.make_get_request("/runs", admin_token)
        self.assert_content_type_and_status(response, 200)
        json_response = response.get_json()
        self.assertEqual(3, json_response['meta']['count'])

        # List for usermananger
        self.create_user("usermanager", admin_token, roles=["usermanager"])
        um_token = self.get_login_token("usermanager")
        response = self.make_get_request("/runs", um_token)
        self.assert_content_type_and_status(response, 200)
        json_response = response.get_json()
        self.assertEqual(0, json_response['meta']['count'])


    def create_user_with_run(self, user_id):
        self.create_user(user_id)
        run_object = deepcopy(sample_run_object)
        run_object['data']['relationships']['user']['data']['id'] = user_id
        user_token = self.get_login_token(user_id)
        response = self.make_post_request("/runs", run_object, user_token)
        self.assert_content_type_and_status(response, 201)
        return user_token

    def test_update_runs(self):
        user = "user1"
        user_token = self.create_user_with_run(user)
        patch_data = {
            "data": {
                "type": "run",
                "id": 1,
                "attributes": {
                    "distance": "4000"
                }
            }
        }

        response = self.make_patch_request('/runs/1', patch_data, user_token)
        self.assert_content_type_and_status(response, 200)

        # user1 trying to update user2
        self.create_user_with_run("user2")
        patch_data['data']['id'] = 2
        response = self.make_patch_request('/runs/2', patch_data, user_token)
        self.assert_content_type_and_status(response, 403)

    def test_update_runs_admin(self):
        user = "user1"
        self.create_user_with_run(user)
        patch_data = {
            "data": {
                "type": "run",
                "id": 1,
                "attributes": {
                    "distance": "4000"
                }
            }
        }
        admin_token = self.get_login_token("admin")

        response = self.make_patch_request('/runs/1', patch_data, admin_token)
        self.assert_content_type_and_status(response, 200)

        # user1 trying to update user2
        self.create_user_with_run("user2")
        patch_data['data']['id'] = 2
        response = self.make_patch_request('/runs/2', patch_data, admin_token)
        self.assert_content_type_and_status(response, 200)

    def test_delete_runs(self):
        user = "user1"
        user_token = self.create_user_with_run(user)
        response = self.make_delete_request('/runs/1', user_token)
        self.assert_content_type_and_status(response, 200)

        # user1 trying to update user2
        self.create_user_with_run("user2")
        response = self.make_delete_request('/runs/2', user_token)
        self.assert_content_type_and_status(response, 403)

    def test_delete_runs_admin(self):
        user = "user1"
        self.create_user_with_run(user)
        admin_token = self.get_login_token("admin")
        response = self.make_delete_request('/runs/1', admin_token)
        self.assert_content_type_and_status(response, 200)

        # user1 trying to update user2
        self.create_user_with_run("user2")
        response = self.make_delete_request('/runs/2', admin_token)
        self.assert_content_type_and_status(response, 200)
















