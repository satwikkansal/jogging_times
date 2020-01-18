from flask_rest_jsonapi import Api, ResourceDetail, ResourceList
from marshmallow import validate
from marshmallow_jsonapi.flask import Schema, Relationship
from marshmallow_jsonapi import fields

from server.models import db, User, Run
from server.utils.decorators import roles_accepted


###
# Data abstractions
###
class UserSchema(Schema):
    id = fields.Str()
    first_name = fields.Str()
    last_name = fields.Str()
    password = fields.Str(required=True, validate=[validate.Length(min=6, max=36)], load_only=True)
    email = fields.Email(allow_none=True, validate=validate.Email(error="Not a valid email address"))
    active = fields.Boolean()
    created_at = fields.Date()

    class Meta:
        type_ = 'user'
        self_view = 'user_detail'
        self_view_kwargs = {'id': '<id>'}
        self_view_many = 'user_list'


class RunSchema(Schema):
    # Dump only can only be applied to auto IDs
    id = fields.Integer(dump_only=True)
    start_time = fields.DateTime()
    end_time = fields.DateTime()
    # Distance in meters
    distance = fields.Integer(as_string=True)
    start_lat = fields.Float(as_string=True)
    start_lng = fields.Float(as_string=True)
    end_lat = fields.Float(as_string=True)
    end_lng = fields.Float(as_string=True)

    class Meta:
        type_ = 'run'
        self_view = 'run_detail'
        # API view url param -> Schema
        self_view_kwargs = {'id': '<id>'}
        self_view_many = 'runs_list'

    user = Relationship(attribute='user',
                        related_view='user_detail',
                        related_view_kwargs={'id': '<user.id>'},
                        schema='UserSchema',
                        type_='user')


###
# Resource endpoints
###
class UserList(ResourceList):
    schema = UserSchema

    """
    @roles_accepted("admin", "usermanager")
    def before_get(*args, **kwargs):
        pass
    """

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
    data_layer = {
        'session': db.session,
        'model': Run
    }


class RunDetail(ResourceDetail):
    schema = RunSchema
    data_layer = {
        'session': db.session,
        'model': User
    }
