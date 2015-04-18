import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    APP_NAME = 'FoodSnag'
    MAILER_NAME = 'Snagger'
    MAILER_EMAIL = 'snagger@foodsnag.com'
    MG_KEY = os.environ.get('MG_KEY')
    MG_URL = 'https://api.mailgun.net/v3/sandbox86fa708b0be84193924a6900094a11cf.mailgun.org'

    SECRET_KEY = os.environ.get('SECRET_KEY') or 'G00DB33F'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')


class TestingConfig(Config):
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data-test.sqlite')


class ProductionConfig(Config):
    MG_URL = 'https://api.mailgun.net/v3/mg.foodsnag.com'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data.sqlite')


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,

    'default': DevelopmentConfig
}
