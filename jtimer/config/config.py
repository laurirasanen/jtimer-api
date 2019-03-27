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

    SQLALCHEMY_DATABASE_URI = f"mysql://{os.environ.get('MYSQL_USERNAME')}:{os.environ.get('MYSQL_PASSWORD')}@{os.environ.get('MYSQL_HOSTNAME')}:{os.environ.get('MYSQL_PORT')}/{os.environ.get('MYSQL_DB_NAME')}"

class Api(object):
    # don't sort json keys
    JSON_SORT_KEYS = False
