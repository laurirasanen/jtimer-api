import os
from contextlib import closing

from flask import current_app

from jtimer.extensions import mysql


def check_tables():
    if os.environ.get("READTHEDOCS") is True:
        return
        
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
                current_app.config["MYSQL_USER"],
                os.environ["RDS_DB_NAME"],
            )
            cursor.execute(query)

            current_app.config["MYSQL_DB"] = os.environ["RDS_DB_NAME"]

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
