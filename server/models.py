###
# DB configurations and models
###
from datetime import datetime

from flask_bcrypt import Bcrypt
from flask_security import SQLAlchemyUserDatastore, RoleMixin, UserMixin, Security
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship


bcrypt = Bcrypt()
db = SQLAlchemy()

# Define models
roles_users = db.Table(
    'roles_users',
    db.Column('user_id', db.String(), db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
)


class BaseMixin(object):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        cols = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        for k, v in cols.items():
            if isinstance(v, datetime):
                cols[k] = v.strftime("%Y-%m-%d %H:%M:%S")
        return cols

    def save(self):
        db.session.add(self)
        db.session.commit()
        return self


class Role(db.Model, BaseMixin, RoleMixin):
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

    def __str__(self):
        return self.name


class User(db.Model, BaseMixin, UserMixin):
    id = db.Column(db.String(255), primary_key=True)
    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255), nullable=False)
    active = db.Column(db.Boolean(), default=True)
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))

    def verify_password(self, password):
        """
        Verifies the password against stored hash.
        :param password:
        :return:
        """
        return bcrypt.check_password_hash(self.password, password)

    def __str__(self):
        return self.user_id


class BlacklistToken(db.Model, BaseMixin):
    """
    Token Model for storing JWT tokens
    """
    token = db.Column(db.String(500), unique=True, nullable=False)

    def __repr__(self):
        return '<id: token: {}'.format(self.token)

    @staticmethod
    def check_blacklist(auth_token):
        # check whether auth token has been blacklisted
        res = BlacklistToken.query.filter_by(token=str(auth_token)).first()
        if res:
            return True
        else:
            return False


# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(datastore=user_datastore)


class Weather(db.Model, BaseMixin):
    pass


class Run(db.Model, BaseMixin):
    user_id = db.Column(db.String, db.ForeignKey(User.id))
    weather_id = db.Column(db.Integer, db.ForeignKey(Weather.id))
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    # Distance in meters
    distance = db.Column(db.Integer)
    start_lat = db.Column(db.String(20))
    start_lng = db.Column(db.String(20))
    end_lat = db.Column(db.String(20))
    end_lng = db.Column(db.String(20))

    user = db.relationship('User', foreign_keys='Run.user_id')
    weather = db.relationship('Weather', foreign_keys='Run.weather_id')
