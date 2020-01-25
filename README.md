# ___Jogging times___
>  A backend project creating REST API that tracks jogging times of users

## About 

- The APIs implemented follow JSON:API specification ([Reference](https://jsonapi.org/)).
- There are two resources the "User" and the "Run", available at the routes `/users` and `/runs` respectively.
- A version of generated API documentation is present [here](https://documenter.getpostman.com/view/689808/SWT8hKzF?version=latest).

## Instructions to run

### With docker (production mode)

The project comes with a docker image which can be deployed to any machine supporting docker.

```bash
# Check-in to the project directory
$ cd jogging-times
# Set the config environment variable and Run the docker containers in daemon mode
$ APP_SETTINGS=server.config.StagingConfig docker-compose up -d
```

This should get the server running at port 5000 (default port). To initialize the db, run

```bash
$ docker-compose exec api python manage.py create_db
```

This will instantiate the roles `user`, `usermanger`, and  `admin`. Also, creates an admin user with login `admin` and password `random` to ease the process of playing around with the documented APIs.

### In development mode

```bash
$ pip install -r requirements.txt
$ python manage.py runserver # Starts the server at port 5000
```

### Running the tests

```bash
$ pip install -r test-requirements.txt
$ pytest tests --cov=server
```

Should produce an output like this,

```bash
➜  jogging_times git:(master) ✗ pytest --cov=server
=========================================================================================== test session starts ============================================================================================
platform darwin -- Python 3.6.9, pytest-5.3.4, py-1.8.1, pluggy-0.13.1
rootdir: /Users/satwik/code/never_see_you_again/jogging_times
plugins: cov-2.8.1
collected 32 items

tests/test_auth.py ...........                                                                                                                                                                       [ 34%]
tests/test_config.py ...                                                                                                                                                                             [ 43%]
tests/test_runs.py ........                                                                                                                                                                          [ 68%]
tests/test_summary.py ....                                                                                                                                                                           [ 81%]
tests/test_users.py ......                                                                                                                                                                           [100%]

---------- coverage: platform darwin, python 3.6.9-final-0 -----------
Name                         Stmts   Miss  Cover
------------------------------------------------
server/__init__.py              20      2    90%
server/config.py                30      0   100%
server/models.py                73      7    90%
server/resources.py            113      3    97%
server/schemas.py               45      0   100%
server/utils/__init__.py         0      0   100%
server/utils/auth_utils.py      19      0   100%
server/utils/weather.py         13      0   100%
server/views.py                 38      2    95%
------------------------------------------------
TOTAL                          351     14    96%

=============================== 32 passed in 8.51s ====================
```

## API Usage

### Authorization

#### `/user/login` (Generate a JWT token)

Sample cURL
```shell script
curl --location --request POST 'localhost:5000/user/login' \
--header 'Content-Type: application/json' \
--data-raw '{
	"user_id": "admin",
	"password": "random"
}'
```

Returns a response of the form,

```json
{
  "auth_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE1Nzk5ODAwODcsIm5iZiI6MTU3OTk4MDA4NywianRpIjoiZDRmNTg0M2ItOWYzOS00M2I0LWFhZTAtMWNlOTc3ODEyMTBhIiwiaWRlbnRpdHkiOiJhZG1pbiIsImZyZXNoIjpmYWxzZSwidHlwZSI6ImFjY2VzcyIsInVzZXJfY2xhaW1zIjp7ImlkIjoiYWRtaW4ifX0.gNSTXq4dy3NPmQKs-widwsLRbmYEI5SW-ypeaNRNLVs",
  "message": "User successfully logged in.",
  "status": "success"
}
```

#### `/user/logout` (Invalidates the JWT token)

```bash
curl --location --request POST 'localhost:5000/user/logout' \
--header 'Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE1Nzk5ODAwODcsIm5iZiI6MTU3OTk4MDA4NywianRpIjoiZDRmNTg0M2ItOWYzOS00M2I0LWFhZTAtMWNlOTc3ODEyMTBhIiwiaWRlbnRpdHkiOiJhZG1pbiIsImZyZXNoIjpmYWxzZSwidHlwZSI6ImFjY2VzcyIsInVzZXJfY2xhaW1zIjp7ImlkIjoiYWRtaW4ifX0.gNSTXq4dy3NPmQKs-widwsLRbmYEI5SW-ypeaNRNLVs'
```

Which should return a response of the form,

```json
{
  "message": "Logged out successfully"
}
```

**Note:** After the JWT token expires (default is 15 min but can be adjusted), you need to login again. 

### `/users`

All the routes in this endpoint return response according to JSON:API specification ([Reference](https://jsonapi.org/)). So the response objects are omitted for brevity.


#### `POST /users` (Create new user)

Sample cuRL,
```sh
curl --location --request POST 'localhost:5000/users' \
--header 'Content-Type: application/json' \
--data-raw '{
	"data": {
		"type": "user",
		"id": "some_user",
		"attributes": {
			"password": "some_user",
			"first_name": "Some first name",
			"last_name": "Some last name",
			"email": "some_user@gmail.com",
			"roles": ["user"]
		}
	}
	
}'
```

- Password should be greater than 6 digits.
- `first_name` and `last_name` are optional.
- `id` and `email` should NOT be already existing in the database.
- `roles` can consist of `admin`, `user` and `usermanager`. More roles can be added by creating entries in `Roles` table in database.
- Creating a user having any of `amdin` or `usermanager` role requires Authorization token of "admin" role.

#### GET /users (Get list of users)

```bash
curl --location --request POST 'localhost:5000/user/list' \
--header 'Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE1NzkxOTg4NzIsIm5iZiI6MTU3OTE5ODg3MiwianRpIjoiNzRkMzM1ZjItZGU5Ni00MzkyLWI0OWQtNDk0ZjhjNTMwOWU3IiwiZXhwIjoxNTc5MTk5NzcyLCJpZGVudGl0eSI6InRlc3Q1IiwiZnJlc2giOmZhbHNlLCJ0eXBlIjoiYWNjZXNzIiwidXNlcl9jbGFpbXMiOnsiaWQiOiJ0ZXN0NSJ9fQ.Vfg4rHLEUO6FayUppBp5TU-sTVJMNxYP_V4GoseSOwY'
```

- `admin` or `usermanager` role will obtain all the users.
- Only `user` role users will obtain just their own record.


#### PATCH /users/{user_id}

```bash
curl --location --request PATCH 'localhost:5000/users/admin' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE1Nzk3MjUxOTAsIm5iZiI6MTU3OTcyNTE5MCwianRpIjoiZTVhYzIyMTMtNGNlYi00NGQ4LWE0MGItOTcxMTVkYzJjNTI5IiwiaWRlbnRpdHkiOiJvbmx5X3VzZXIiLCJmcmVzaCI6ZmFsc2UsInR5cGUiOiJhY2Nlc3MiLCJ1c2VyX2NsYWltcyI6eyJpZCI6Im9ubHlfdXNlciJ9fQ.45m7Dqib7OkY2R9d72vfpTxqYxRpx-x6PcMnnyfZQa8' \
--data-raw '{
	"data":  {
		"type": "user",
		"id": "admin",
		"attributes": {
			"first_name": "My updated first name"
		}
	}
	
}'
```

- `admin` or `usermanager` can update any user (including themselves). The `user` role can update only itself.

#### DELETE /users/{user_id}

```bash
curl --location --request PATCH 'localhost:5000/users/some_user' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE1Nzk3MjUxOTAsIm5iZiI6MTU3OTcyNTE5MCwianRpIjoiZTVhYzIyMTMtNGNlYi00NGQ4LWE0MGItOTcxMTVkYzJjNTI5IiwiaWRlbnRpdHkiOiJvbmx5X3VzZXIiLCJmcmVzaCI6ZmFsc2UsInR5cGUiOiJhY2Nlc3MiLCJ1c2VyX2NsYWltcyI6eyJpZCI6Im9ubHlfdXNlciJ9fQ.45m7Dqib7OkY2R9d72vfpTxqYxRpx-x6PcMnnyfZQa8' \
--data-raw ''
```

- `admin` or `usermanager` can delete any user (including themselves). The `user` role can only delete itself.

### `/runs`


#### POST `/runs` Create new run
    
Sample cURL
```bash
curl --location --request POST 'localhost:5000/runs' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE1Nzk4ODI1OTgsIm5iZiI6MTU3OTg4MjU5OCwianRpIjoiMWFkMjY4MjUtNThiNi00Yzk2LWE5OWMtZmZmOTE4YTMwMTdhIiwiaWRlbnRpdHkiOiJ0ZXN0MTMiLCJmcmVzaCI6ZmFsc2UsInR5cGUiOiJhY2Nlc3MiLCJ1c2VyX2NsYWltcyI6eyJpZCI6InRlc3QxMyJ9fQ.dky8KK7Nq6hHrAyrsWBWBpHLPuD32STiP7CdKjj8VBk' \
--data-raw '{
	"data": {
		"type": "run",
		"attributes": {
		        "distance": "4200",
                "start_lat": "12.8947909",
                "start_lng": "77.6427151",
                "end_time": "2020-01-24T16:58:45.838199+00:00",
                "start_time": "2020-01-24T16:34:34.838199+00:00",
                "end_lat": "12.8986343",
                "end_lng": "77.656089"
		},
		"relationships": {
			"user": {
				"data": {
					"type": "user",
					"id": "test13"
				}
			}
		}
	}
	
}'
```

- Creates a run with a relationship to the specified user. Returns an error response if the user doesn't exist.
- Admin has CRUD access for everything, other roles can only CRUD themselves.

#### GET `/runs` (Get list of runs)

Works in a similar way to GET `/users` endpoint, except that the `usermanager` role doesn't have any special privilege here. 

#### PATCH `/runs/{run_id}` (Update run)

Works in a similar way to GET `/users` endpoint, except that the `usermanager` role doesn't have any special privilege here. 

#### DELETE `/runs/{run_id}` (Delete run)

Works in a similar way to GET `/users` endpoint, except that the `usermanager` role doesn't have any special privilege here. 

#### GET `/runs/summary` (Generate weekly summary report)

```bash
curl --location --request GET 'localhost:5000/runs/summary' \
--header 'Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE1Nzk4ODI1OTgsIm5iZiI6MTU3OTg4MjU5OCwianRpIjoiMWFkMjY4MjUtNThiNi00Yzk2LWE5OWMtZmZmOTE4YTMwMTdhIiwiaWRlbnRpdHkiOiJ0ZXN0MTMiLCJmcmVzaCI6ZmFsc2UsInR5cGUiOiJhY2Nlc3MiLCJ1c2VyX2NsYWltcyI6eyJpZCI6InRlc3QxMyJ9fQ.dky8KK7Nq6hHrAyrsWBWBpHLPuD32STiP7CdKjj8VBk'
```

Returns response of the form,

```json
{
    "data": [
        {
            "type": "report",
            "attributes": {
                "year": 2020,
                "week_number": 4,
                "average_distance": "7500.0",
                "average_duration": "1500.0",
                "average_speed": "4.5"
            }
        },
        {
            "type": "report",
            "attributes": {
                "year": 2020,
                "week_number": 3,
                "average_distance": "15000.0",
                "average_duration": "4800.0",
                "average_speed": "3.0"
            }
        }
    ],
    "links": {
        "self": "http://localhost/runs/summary"
    },
    "meta": {
        "count": 2
    },
    "jsonapi": {
        "version": "1.0"
    }
}
```

### API Pagination and filtering.

The API supports json-based-filtering and pagination of results. Some examples of the URLs,

* `http://localhost:5000/runs?filter[user_id]=test11&page[size]=1&page[number]=2` 

Get all runs of user `test11`, keep page size to 10, and fetch page 2.

* `http://localhost:5000/runs?filter=[{"and": [{"name": "start_time", "op": "ge", "val": "2020-01-21"}, {"name": "user_id", "op": "eq", "val": "test11"}]}]`

Runs on or after 21st Jan 2020 by user `test11`


## Progress


| Task          |    Status     | Remarks  |
| ------------- |:-------------:| ---------|
| API Users must be able to create an account and log in. | [ x ] | All the APIs have JWT-based authorization (except for create new user API) |
| Implement at least three roles with different permission levels: a regular user would only be able to CRUD on their owned records, a user manager would be able to CRUD only users, and an admin would be able to CRUD all records and users. | [ x ] | Three roles implemented; "amdin", "usermanager", and a "user". API can be extended to new roles by creating role entries in the Database. |
| Each time entry when entered has a date, distance, time, and location. | [ x ] | Each run will have all the mentioned information.
| The API should provide filter capabilities for all endpoints that return a list of elements, as well should be able to support pagination. | [ x ] | The API supports JSON-object based filtering used in frameworks like [flask-restless](https://flask-restless.readthedocs.io/en/latest/filtering.html). |
| Based on the provided date and location, API should connect to a weather API provider and get the weather conditions for the run, and store that with each run. | [ x ] | Weather information is fetched based on the end_time of the run and stored as JSON in a separate field. The project uses [Open Weather Map API](https://openweathermap.org/api) to get the weather details. |
| The API must create a report on average speed & distance per week. | [ x ] | There's a special endpoint called `/runs/summary` for exactly this. The user information is taken from the JWT token for the API. |
| The API should provide filter capabilities for all endpoints that return a list of elements, as well should be able to support pagination. | [ x ] | The APIs support both pagination and filtering. |
| The API filtering should allow using parenthesis for defining operations precedence and use any combination of the available fields. The supported operations should at least include or, and, eq (equals), ne (not equals), gt (greater than), lt (lower than). Example -> (date eq '2016-05-01') AND ((distance gt 20) OR (distance lt 10)). | [ x ] | The JSON-based object filtering uses JSON objects which can be nested and logically combined. |
| Write Unit tests | [ x ] | Unit tests available in `tests` directory. |