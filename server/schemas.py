from marshmallow import validate
from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Schema, Relationship

###
# Data abstractions
###


class UserSchema(Schema):
    id = fields.Str()
    first_name = fields.Str()
    last_name = fields.Str()
    password = fields.Str(required=True, validate=[validate.Length(min=6, max=36)], load_only=True)
    email = fields.Email(allow_none=True, validate=validate.Email(error="Not a valid email address"))
    roles = fields.List(fields.String())
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
    user_id = fields.String(load_only=True)
    start_time = fields.DateTime(required=True)
    end_time = fields.DateTime(required=True)
    date = fields.String(dump_only=True)
    # Distance in meters
    distance = fields.Integer(required=True, as_string=True)
    start_lat = fields.Float(required=True, as_string=True)
    start_lng = fields.Float(required=True, as_string=True)
    end_lat = fields.Float(required=True, as_string=True)
    end_lng = fields.Float(required=True, as_string=True)
    weather_info = fields.String(dump_only=True)

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