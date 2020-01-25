from datetime import datetime


from tests.base import BaseTestCase


class TestRunSummary(BaseTestCase):
    date_format = "%Y-%m-%dT%H:%M"

    def create_run_object(self, distance, start_time, end_time, user_id):
        self.create_user(user_id)
        utoken = self.get_login_token(user_id)
        run_object = {
            "data": {
                "type": "run",
                "attributes": {
                    "start_time": start_time.astimezone().isoformat(),
                    "end_time": end_time.astimezone().isoformat(),
                    "start_lat": "12.8947909",
                    "start_lng": "77.6427151",
                    "end_lat": "12.8986343",
                    "end_lng": "77.656089",
                    "distance": str(distance)
                },
                "relationships": {
                    "user": {
                        "data": {
                            "type": "user",
                            "id": user_id
                        }
                    }
                }
            }
        }
        response = self.make_post_request("/runs", run_object, utoken)
        self.assert_content_type_and_status(response, 201)
        return utoken

    def test_summary_report(self):
        user1_token = self.create_run_object(
            5000,
            datetime.strptime("2020-01-20T16:34", self.date_format),
            datetime.strptime("2020-01-20T16:54", self.date_format),
            "user1")
        self.create_run_object(
            10000,
            datetime.strptime("2020-01-20T16:24", self.date_format),
            datetime.strptime("2020-01-20T16:54", self.date_format),
            "user1")

        response = self.make_get_request("/runs/summary", user1_token)
        self.assert_content_type_and_status(response, 200)
        json_response = response.get_json()
        data = json_response["data"]
        meta = json_response["meta"]
        self.assertEqual(1, meta.get("count"))
        latest_week_data = data[0]["attributes"]
        self.assertEqual(4.5, float(latest_week_data["average_speed"]))
        self.assertEqual(7500.0, float(latest_week_data["average_distance"]))
        self.assertEqual(1500.0, float(latest_week_data["average_duration"]))
        self.assertEqual(2020, latest_week_data["year"])
        self.assertEqual(4, latest_week_data["week_number"])

    def test_summary_report_multiple_weeks(self):
        # Multiple weeks
        user1_token = self.create_run_object(
            15000,
            datetime.strptime("2020-01-14T15:34", self.date_format),
            datetime.strptime("2020-01-14T16:54", self.date_format),
            "user1")
        self.create_run_object(
            10000,
            datetime.strptime("2020-01-23T16:24", self.date_format),
            datetime.strptime("2020-01-23T16:54", self.date_format),
            "user1")
        self.create_run_object(
            5000,
            datetime.strptime("2020-01-23T16:34", self.date_format),
            datetime.strptime("2020-01-23T16:54", self.date_format),
            "user1")
        response = self.make_get_request("/runs/summary", user1_token)
        self.assert_content_type_and_status(response, 200)
        json_response = response.get_json()
        data = json_response["data"]
        meta = json_response["meta"]
        self.assertEqual(2, meta.get("count"))
        latest_week_data = data[0]["attributes"]
        self.assertEqual(4.5, float(latest_week_data["average_speed"]))
        self.assertEqual(7500.0, float(latest_week_data["average_distance"]))
        self.assertEqual(1500.0, float(latest_week_data["average_duration"]))
        self.assertEqual(2020, latest_week_data["year"])
        self.assertEqual(4, latest_week_data["week_number"])

        second_last_week_data = data[1]["attributes"]
        self.assertEqual(3.0, float(second_last_week_data["average_speed"]))
        self.assertEqual(15000.0, float(second_last_week_data["average_distance"]))
        self.assertEqual(4800.0, float(second_last_week_data["average_duration"]))
        self.assertEqual(2020, second_last_week_data["year"])
        self.assertEqual(3, second_last_week_data["week_number"])

    def test_summary_report_multiple_users(self):
        user1_token = self.create_run_object(
            5000,
            datetime.strptime("2020-01-20T16:34", self.date_format),
            datetime.strptime("2020-01-20T16:54", self.date_format),
            "user1")
        self.create_run_object(
            10000,
            datetime.strptime("2020-01-20T16:24", self.date_format),
            datetime.strptime("2020-01-20T16:54", self.date_format),
            "user1")

        user2_token = self.create_run_object(
            15000,
            datetime.strptime("2020-01-14T15:34", self.date_format),
            datetime.strptime("2020-01-14T16:54", self.date_format),
            "user2")
        self.create_run_object(
            10000,
            datetime.strptime("2020-01-23T16:24", self.date_format),
            datetime.strptime("2020-01-23T16:54", self.date_format),
            "user2")
        self.create_run_object(
            5000,
            datetime.strptime("2020-01-23T16:34", self.date_format),
            datetime.strptime("2020-01-23T16:54", self.date_format),
            "user2")

        # Verify user 1 stats
        response = self.make_get_request("/runs/summary", user1_token)
        self.assert_content_type_and_status(response, 200)
        json_response = response.get_json()
        data = json_response["data"]
        meta = json_response["meta"]
        self.assertEqual(1, meta.get("count"))
        latest_week_data = data[0]["attributes"]
        self.assertEqual(4.5, float(latest_week_data["average_speed"]))
        self.assertEqual(7500.0, float(latest_week_data["average_distance"]))
        self.assertEqual(1500.0, float(latest_week_data["average_duration"]))
        self.assertEqual(2020, latest_week_data["year"])
        self.assertEqual(4, latest_week_data["week_number"])

        # Verify user 2 stats
        response = self.make_get_request("/runs/summary", user2_token)
        self.assert_content_type_and_status(response, 200)
        json_response = response.get_json()
        data = json_response["data"]
        meta = json_response["meta"]
        self.assertEqual(2, meta.get("count"))
        latest_week_data = data[0]["attributes"]
        self.assertEqual(4.5, float(latest_week_data["average_speed"]))
        self.assertEqual(7500.0, float(latest_week_data["average_distance"]))
        self.assertEqual(1500.0, float(latest_week_data["average_duration"]))
        self.assertEqual(2020, latest_week_data["year"])
        self.assertEqual(4, latest_week_data["week_number"])



    def test_summary_create(self):
        # It shouldn't be allowed
        response = self.make_post_request("/runs/summary", {})
        self.assert_content_type_and_status(response, 405)