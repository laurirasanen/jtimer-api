from jtimer.models.database.players import (
    find_player as db_find_player,
    list_players as db_list_players,
)


class Player:
    def __init__(
        self,
        playerid,
        steamid,
        name,
        soldier_points,
        demo_points,
        soldier_rank,
        demo_rank,
    ):
        self.playerid = playerid
        self.name = name
        self.steamid = steamid
        self.soldier_points = soldier_points
        self.demo_points = demo_points
        self.soldier_rank = soldier_rank
        self.demo_rank = demo_rank

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
    player = None
    player_class = None
    if playerid != None:
        player = db_find_player(playerid=playerid)

    elif steamid != None:
        player = db_find_player(steamid=steamid)

    elif name != None:
        player = db_find_player(name=name)

    if player != None:
        player_class = Player(
            player[0], player[1], player[2], player[3], player[4], player[5], player[6]
        )

    return player_class


def list_players(limit=50, start=0):
    players = db_list_players(limit=limit, start=start)
    players_list = []
    if players != None:
        for i in range(0, len(players)):
            players_list.append(
                Player(
                    players[i][0],
                    players[i][1],
                    players[i][2],
                    players[i][3],
                    players[i][4],
                    players[i][5],
                    players[i][6],
                )
            )
    return players_list
