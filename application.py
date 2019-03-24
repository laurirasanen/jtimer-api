import os
import json
import signal
from configparser import ConfigParser
from contextlib import closing

from flask import Flask, request, make_response, jsonify
from flask_mysqldb import MySQL

application = Flask(__name__)

if "RDS_HOSTNAME" in os.environ:
    application.config["MYSQL_HOST"] = os.environ["RDS_HOSTNAME"]
    application.config["MYSQL_PORT"] = int(os.environ["RDS_PORT"])
    application.config["MYSQL_USER"] = os.environ["RDS_USERNAME"]
    application.config["MYSQL_PASSWORD"] = os.environ["RDS_PASSWORD"]

mysql = MySQL(application)

config = ConfigParser()


@application.route("/", methods=["GET", "POST", "PUT"])
def index():
    return make_response(
        "http://github.com/occasionally-cool/jtimer-beanstalk-api", 418
    )  # I'm a teapot


@application.route("/info", methods=["GET"])
@application.route("/version", methods=["GET"])
def info():
    config.read("info.ini")
    info = {}
    info["version"] = config.get("root", "version", fallback=None)
    info["source"] = config.get("root", "source", fallback=None)
    return make_response(jsonify(info), 200)


@application.route("/players/list", methods=["GET"])
def list_players():
    players = None
    if mysql.connection != None:
        with closing(mysql.connection.cursor()) as cursor:
            cursor.execute("""SELECT * FROM players""")
            players = cursor.fetchall()

    if players == None:
        return make_response("Could not load players", 500)
    else:
        players_list = []
        for p in players:
            player_entry = {
                "id": p[0],
                "steamid": p[1],
                "name": p[2],
                "rank_info": {
                    "soldier_rank": p[3],
                    "demo_rank": p[4],
                    "soldier_points": p[5],
                    "demo_points": p[6]
                }
            }
            players_list.append(player_entry)
        return make_response(jsonify(players_list), 200)


@application.before_first_request
def check_tables():
    if mysql.connection != None:
        with closing(mysql.connection.cursor()) as cursor:
            query = """
                CREATE DATABASE IF NOT EXISTS %s;
                GRANT ALL PRIVILEGES ON %s.* to %s@'%%';
                FLUSH PRIVILEGES;
                USE %s;
                """
            query = query % (
                os.environ["RDS_DB_NAME"],
                os.environ["RDS_DB_NAME"],
                application.config["MYSQL_USER"],
                os.environ["RDS_DB_NAME"]
            )
            cursor.execute(query)

            application.config["MYSQL_DB"] = os.environ["RDS_DB_NAME"]

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS players(
                    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                    steamid TEXT NOT NULL,
                    username TEXT NOT NULL,
                    srank INT NOT NULL DEFAULT 0,
                    drank INT NOT NULL DEFAULT 0,
                    spoints DOUBLE NOT NULL DEFAULT 0.00,
                    dpoints DOUBLE NOT NULL DEFAULT 0.00
                );
                CREATE TABLE IF NOT EXISTS zones(
                    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                    x1 INT NOT NULL,
                    z1 INT NOT NULL,
                    y1 INT NOT NULL,
                    x2 INT NOT NULL,
                    z2 INT NOT NULL,
                    y2 INT NOT NULL
                );    
                CREATE TABLE IF NOT EXISTS maps(
                    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                    mapname TEXT NOT NULL,
                    stier INT NOT NULL DEFAULT 0,
                    dtier INT NOT NULL DEFAULT 0,
                    completions INT NOT NULL DEFAULT 0,
                    startzone INT NOT NULL,
                    endzone INT NOT NULL,
                    FOREIGN KEY (startzone) REFERENCES zones(id), 
                    FOREIGN KEY (endzone) REFERENCES zones(id)
                );   
                CREATE TABLE IF NOT EXISTS authors(
                    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                    playerid INT NOT NULL,
                    mapid INT NOT NULL,
                    FOREIGN KEY (playerid) REFERENCES players(id),
                    FOREIGN KEY (mapid) REFERENCES maps(id)
                );         
                CREATE TABLE IF NOT EXISTS courses(
                    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                    mapid INT NOT NULL,
                    FOREIGN KEY (mapid) REFERENCES maps(id),
                    courseindex INT NOT NULL,
                    stier INT NOT NULL DEFAULT 0,
                    dtier INT NOT NULL DEFAULT 0,
                    completions INT NOT NULL DEFAULT 0,
                    startzone INT NOT NULL,
                    endzone INT NOT NULL,
                    FOREIGN KEY (startzone) REFERENCES zones(id),
                    FOREIGN KEY (endzone) REFERENCES zones(id)
                );
                CREATE TABLE IF NOT EXISTS bonuses(
                    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                    mapid INT NOT NULL,
                    FOREIGN KEY (mapid) REFERENCES maps(id),
                    bonusindex INT NOT NULL,
                    stier INT NOT NULL DEFAULT 0,
                    dtier INT NOT NULL DEFAULT 0,
                    completions INT NOT NULL DEFAULT 0,
                    startzone INT NOT NULL,
                    endzone INT NOT NULL,
                    FOREIGN KEY (startzone) REFERENCES zones(id),
                    FOREIGN KEY (endzone) REFERENCES zones(id)
                );
                CREATE TABLE IF NOT EXISTS mapcheckpoints(
                    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                    zoneid INT NOT NULL,
                    mapid INT NOT NULL,
                    FOREIGN KEY (zoneid) REFERENCES zones(id),
                    FOREIGN KEY (mapid) REFERENCES maps(id),
                    cpindex INT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS coursecheckpoints(
                    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                    zoneid INT NOT NULL,
                    courseid INT NOT NULL,
                    FOREIGN KEY (zoneid) REFERENCES zones(id),
                    FOREIGN KEY (courseid) REFERENCES courses(id),
                    cpindex INT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS bonuscheckpoints(
                    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                    zoneid INT NOT NULL,
                    bonusid INT NOT NULL,
                    FOREIGN KEY (zoneid) REFERENCES zones(id),
                    FOREIGN KEY (bonusid) REFERENCES bonuses(id),
                    cpindex INT NOT NULL
                );
                """
            )
        mysql.connection.commit()


def receiveSIGTERM():
    print("Received SIGTERM")
    mysql.connection.close()


if __name__ == "__main__":
    signal.signal(signal.SIGTERM, receiveSIGTERM)

    application.run(debug=True, host="127.0.0.1")
