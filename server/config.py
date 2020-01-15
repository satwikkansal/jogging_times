import os
basedir = os.path.abspath(os.path.dirname(__file__))
postgres_local_base = 'postgresql://localhost/'
database_name = 'jogging_times'


class BaseConfig:
    """
    Base configuration.
    """
    JWT_SECRET_KEY = os.getenv('SECRET_KEY', 'some_secret')
    DEBUG = False
    BCRYPT_LOG_ROUNDS = 13
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECURITY_TRACKABLE= True
    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = ['access']


class DevelopmentConfig(BaseConfig):
    """
    Development configuration.
    """
    DEBUG = True
    BCRYPT_LOG_ROUNDS = 4
    SQLALCHEMY_DATABASE_URI = postgres_local_base + database_name


class TestingConfig(BaseConfig):
    """
    Testing configuration.
    """
    DEBUG = True
    TESTING = True
    BCRYPT_LOG_ROUNDS = 4
    SQLALCHEMY_DATABASE_URI = postgres_local_base + database_name + '_test'
    PRESERVE_CONTEXT_ON_EXCEPTION = False


class ProductionConfig(BaseConfig):
    """
    Production configuration.
    """
    SECRET_KEY = 'some_secret'
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = 'postgresql://' + database_name
