import os


class MySQL(object):
    # make sure variables are set to something,
    # so we don't get errors while building docs
    if os.environ.get("RDS_HOSTNAME") is not None:
        MYSQL_HOST = os.environ.get("RDS_HOSTNAME")
    else:
        MYSQL_HOST = "localhost"

    if os.environ.get("RDS_PORT") is not None:
        MYSQL_PORT = int(os.environ.get("RDS_PORT"))
    else:
        MYSQL_PORT = 3306

    if os.environ.get("RDS_USERNAME") is not None:
        MYSQL_USER = os.environ.get("RDS_USERNAME")
    else:
        MYSQL_USER = "jtimer"

    if os.environ.get("RDS_PASSWORD") is not None:
        MYSQL_PASSWORD = os.environ.get("RDS_PASSWORD")
    else:
        MYSQL_PASSWORD = "foo"

    if os.environ.get("RDS_DB_NAME") is None:
        os.environ["RDS_DB_NAME"] = "jtimerdb"
