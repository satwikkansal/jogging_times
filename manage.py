# manage.py

import os
import unittest

import coverage
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

from server import app
from server.models import db, Role, User

migrate = Migrate(app, db)
manager = Manager(app)

# migrations
manager.add_command('db', MigrateCommand)


@manager.command
def test():
    """
    Runs the unit tests without test coverage.
    """
    tests = unittest.TestLoader().discover('./tests', pattern='test*.py')
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        return 0
    return 1


@manager.command
def cov():
    """
    Runs the unit tests with coverage.
    """
    COV = coverage.coverage(
        branch=True,
        include='server/*',
        omit=[
            'server/tests/*',
            'server/config.py'
        ]
    )

    COV.start()
    tests = unittest.TestLoader().discover('./tests')
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        COV.stop()
        COV.save()
        print('Coverage Summary:')
        COV.report()
        basedir = os.path.abspath(os.path.dirname(__file__))
        covdir = os.path.join(basedir, 'tmp/coverage')
        COV.html_report(directory=covdir)
        print('HTML version: file://%s/index.html' % covdir)
        COV.erase()
        return 0
    return 1


@manager.command
def create_db():
    """
    Creates the db tables.
    """
    db.create_all()
    populate_roles()
    create_admin_user()


@manager.command
def drop_db():
    """
    Drops the db tables.
    """
    db.drop_all()


def populate_roles():
    Role(name="admin", description="Admin role", privileged=True).save()
    Role(name="usermanager", description="User Manager role", privileged=True).save()
    Role(name="user", description="User role").save()


def create_admin_user():
    User(id='admin',
         password=User.get_password_hash("random"),
         email="admin@testmail.com",
         roles=[Role.query.filter_by(name="admin").first()]).save()


if __name__ == '__main__':
    manager.run()
