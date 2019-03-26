from jtimer.models.database.players import (
    find_player as db_find_player,
    list_players as db_list_players,
)


class Player:
    def __init__(self, playerid, steamid, name, soldier_points, demo_points):
        self.playerid = playerid
        self.name = name
        self.steamid = steamid
        self.soldier_points = soldier_points
        self.demo_points = demo_points
        self.soldier_rank = 0
        self.demo_rank = 0

    def get_object(self):
        obj = {
            "id": self.playerid,
            "name": self.name,
            "steamid": self.steamid,
            "rank_info": {
                "soldier_points": self.soldier_points,
                "demo_points": self.demo_points,
                "soldier_rank": self.soldier_rank,
                "demo_rank": self.demo_rank,
            },
        }
        return obj


def find_player(playerid=None, steamid=None, name=None):
    if playerid != None:
        result = db_find_player(playerid=playerid)

    elif steamid != None:
        result = db_find_player(steamid=steamid)

    elif name != None:
        result = db_find_player(name=name)

    for row in result:
        return Player(
            row["id"], row["steamid"], row["username"], row["spoints"], row["dpoints"]
        )

    return None


def list_players(limit=50, start=0):
    result = db_list_players(limit=limit, start=start)
    players_list = []

    for row in result:
        players_list.append(
            Player(
                row["id"],
                row["steamid"],
                row["username"],
                row["spoints"],
                row["dpoints"],
            )
        )

    return players_list
