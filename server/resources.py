from flask_jwt_extended import get_jwt_claims
from flask_rest_jsonapi import Api, ResourceDetail, ResourceList, JsonApiException
from marshmallow_jsonapi.flask import Schema
from marshmallow_jsonapi import fields
from sqlalchemy import func

from server.models import db, User, Run, Role, user_datastore
from server.schemas import UserSchema, RunSchema
from server.utils.decorators import roles_accepted, get_user_from_jwt, \
    raise_permission_denied_exception

from server.utils.weather import get_current_weather_at_location

api = Api()


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

    def query(self, view_kwargs):
        """
        Restricts results for GET requests.
        """
        query_ = self.session.query(User)
        user = get_user_from_jwt()
        if not user.is_privileged():
            query_ = query_.filter(User.id == user.id)
        return query_

    def before_post(*args, **kwargs):
        """
        Validates authorization for POST requests.
        """
        data = kwargs['data']
        privileged_roles = [role.name for role in Role.query.filter_by(privileged=True).all()]
        if list(set(privileged_roles) & set(data['roles'])):
            # Only Admin can create privileged users.
            user = get_user_from_jwt()
            if not user or not user.has_role("admin"):
                raise_permission_denied_exception(
                    "Only admins can create users with privileged roles"
                )

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
                e.title = "The user_id or email already exists."
            raise e

    data_layer = {
        'session': db.session,
        'model': User,
        'methods': {
            'query': query
        }
    }


class UserDetail(ResourceDetail):
    def self_or_privileged_user(view_id):
        user = get_user_from_jwt()
        return user.is_privileged() or user.id == view_id

    def is_allowed_to_modify(user_to_modify):
        user = get_user_from_jwt()
        if user.has_role("admin") or user.id == user_to_modify.id:
            return True
        if user.has_role("usermanager"):
            modifying_privileged_user = user_to_modify.is_privileged()
            return False if modifying_privileged_user else True
        return False

    def before_get_object(self, view_kwargs):
        if not UserDetail.self_or_privileged_user(view_kwargs.get('id')):
            raise_permission_denied_exception("User doesn't have permission to access the resource.")

    def before_update_object(self, obj, data, view_kwargs):
        if not UserDetail.is_allowed_to_modify(obj):
            raise_permission_denied_exception("User doesn't have permission to access the resource.")

    def before_delete_object(self, obj, view_kwargs):
        if not UserDetail.is_allowed_to_modify(obj):
            raise_permission_denied_exception("User doesn't have permission to access the resource.")

    schema = UserSchema
    data_layer = {
        'session': db.session,
        'model': User,
        'methods': {
            'before_get_object': before_get_object,
            'before_update_object': before_update_object,
            'before_delete_object': before_delete_object
        }
    }


class RunsList(ResourceList):
    schema = RunSchema

    @roles_accepted("user")
    def before_get(self, args, kwargs):
        pass

    @roles_accepted("user")
    def before_patch(self, args, kwargs):
        pass

    @roles_accepted("user")
    def before_delete(self, args, kwargs):
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
