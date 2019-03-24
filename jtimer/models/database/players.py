from contextlib import closing

from jtimer.extensions import mysql


def list_players(start=0, limit=50):
    players = None
    if mysql.connection != None:
        with closing(mysql.connection.cursor()) as cursor:
            cursor.execute(
                """SELECT * FROM players LIMIT %s OFFSET %s""", (limit, start)
            )
            players = cursor.fetchall()

    return players


def find_player(playerid=None, steamid=None, name=None):
    player = None

    if playerid != None:
        if mysql.connection != None:
            with closing(mysql.connection.cursor()) as cursor:
                cursor.execute(
                    """SELECT * FROM players WHERE id=%s LIMIT 1""", (playerid,)
                )
                player = cursor.fetchone()

    elif steamid != None:
        if mysql.connection != None:
            with closing(mysql.connection.cursor()) as cursor:
                cursor.execute(
                    """SELECT * FROM players WHERE steamid=%s LIMIT 1""", (steamid,)
                )
                player = cursor.fetchone()

    elif name != None:
        if mysql.connection != None:
            with closing(mysql.connection.cursor()) as cursor:
                cursor.execute(
                    """SELECT * FROM players WHERE username=%s LIMIT 1""", (name,)
                )
                player = cursor.fetchone()

    return player
