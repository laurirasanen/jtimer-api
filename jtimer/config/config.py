import os


class MySQL(object):
    # make sure variables are set to something,
    # so we don't get errors while building docs

    if os.environ.get("MYSQL_HOSTNAME") is None:
        os.environ["MYSQL_HOSTNAME"] = "localhost"

    if os.environ.get("MYSQL_PORT") is None:
        os.environ["MYSQL_PORT"] = "3306"

    if os.environ.get("MYSQL_USERNAME") is None:
        os.environ["MYSQL_USERNAME"] = "jtimer"

    if os.environ.get("MYSQL_PASSWORD") is None:
        os.environ["MYSQL_PASSWORD"] = "foo"

    if os.environ.get("MYSQL_DB_NAME") is None:
        os.environ["MYSQL_DB_NAME"] = "jtimerdb"

    SQLALCHEMY_DATABASE_URI = (
        f"mysql://{os.environ.get('MYSQL_USERNAME')}"
        + f":{os.environ.get('MYSQL_PASSWORD')}"
        + f"@{os.environ.get('MYSQL_HOSTNAME')}"
        + f":{os.environ.get('MYSQL_PORT')}"
        + f"/{os.environ.get('MYSQL_DB_NAME')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class Api(object):
    # don't sort json keys
    JSON_SORT_KEYS = False

    if not os.environ.get("READTHEDOCS"):
        assert os.environ.get("SECRET_KEY") != None
        SECRET_KEY = os.environ.get("SECRET_KEY").encode()

        assert os.environ.get("JWT_SECRET_KEY") != None
        JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY")

    JWT_ACCESS_TOKEN_EXPIRES = 60 * 60
    JWT_REFRESH_TOKEN_EXPIRES = 60 * 60 * 24
    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = ["access", "refresh"]
