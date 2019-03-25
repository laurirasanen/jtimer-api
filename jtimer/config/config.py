import os


class MySQL(object):
    MYSQL_HOST = os.environ["RDS_HOSTNAME"]
    MYSQL_PORT = int(os.environ["RDS_PORT"])
    MYSQL_USER = os.environ["RDS_USERNAME"]
    MYSQL_PASSWORD = os.environ["RDS_PASSWORD"]
