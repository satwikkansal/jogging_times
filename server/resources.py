from flask_jwt_extended import get_jwt_claims
from flask_rest_jsonapi import ResourceDetail, ResourceList, JsonApiException
from marshmallow_jsonapi.flask import Schema
from marshmallow_jsonapi import fields
from sqlalchemy import func

from server.models import db, User, Run, Role
from server.schemas import UserSchema, RunSchema
from server.utils.decorators import roles_accepted

from server.utils.weather import get_current_weather_at_location


class WeeklyRunsReport(Schema):
    id = fields.Integer(dump_only=True)
    average_speed = fields.Float(as_string=True, dump_only=True)
    average_distance = fields.Float(as_string=True, dump_only=True)
    average_duration = fields.Float(as_string=True, dump_only=True)
    week_number = fields.Integer()
    year = fields.Integer()

    class Meta:
        type_ = 'report'
        self_view_many = 'weekly_summary'


###
# Resource endpoints
###
class UserList(ResourceList):
    schema = UserSchema

    @roles_accepted("admin", "usermanager")
    def before_get(*args, **kwargs):
        pass

    @roles_accepted("admin", "usermanager")
    def before_post(*args, **kwargs):
        pass

    def create_object(self, data, kwargs):
        password = data['password'].encode('utf-8')
        data['password'] = User.get_password_hash(password)

        role_objects = []
        for role in data['roles']:
            role_objects.append(Role.query.filter_by(name=role).first())
        data['roles'] = role_objects
        try:
            return self._data_layer.create_object(data, kwargs)
        except JsonApiException as e:
            if 'psycopg2.errors.UniqueViolation' in str(e):
                e.status = 409
                e.title = "The user_id already exists."
            raise e

    data_layer = {
        'session': db.session,
        'model': User
    }


class UserDetail(ResourceDetail):
    """
    @roles_accepted("admin", "usermanager", "user")
    def before_post(*args, **kwargs):
        pass

    @roles_accepted("admin", "usermanager", "user")
    def before_get(*args, **kwargs):
        pass
    """

    schema = UserSchema
    data_layer = {
        'session': db.session,
        'model': User
    }


class RunsList(ResourceList):
    schema = RunSchema

    @roles_accepted("user")
    def before_get(self, args, kwargs):
        pass

    def query(self, view_kwargs):
        query_ = self.session.query(Run)
        user_id = get_jwt_claims().get('id')
        if user_id is None:
            raise ValueError("No ID found in the JWT token claims")
        return query_.filter(Run.user_id == user_id)

    def create_object(self, data, kwargs):
        lat, lng = data['end_lat'], data['end_lng']
        data['weather_info'] = get_current_weather_at_location(lat, lng)
        data['date'] = data['start_time'].strftime("%Y-%m-%d")
        return self._data_layer.create_object(data, kwargs)

    data_layer = {
        'session': db.session,
        'model': Run,
        'methods': {
            'query': query
        }
    }


class WeeklySummary(ResourceList):
    schema = WeeklyRunsReport

    def query(self, view_kwargs):
        week_number = func.date_part('week', Run.start_time)
        year = func.date_part('year', Run.start_time)
        query_ = self.session.query(
            func.avg(Run.distance).label('average_distance'),
            func.avg(Run.duration).label('average_duration'),
            func.avg(Run.distance / Run.duration).label('average_speed'),
            week_number.label('week_number'),
            year.label('year')
        ).group_by(year, week_number)
        return query_

    data_layer = {
        'session': db.session,
        'model': Run,
        'methods': {
            'query': query
        }
    }


class RunDetail(ResourceDetail):
    schema = RunSchema
    data_layer = {
        'session': db.session,
        'model': User
    }
