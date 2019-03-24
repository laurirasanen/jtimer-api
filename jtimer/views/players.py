from flask import jsonify, make_response, request
from jtimer.blueprints import players_index
from jtimer.models.player import (
    list_players as mdl_list_players,
    find_player as mdl_find_player,
)


@players_index.route("/list")
def list_players():
    limit = request.args.get("limit", default=50, type=int)
    start = request.args.get("start", default=0, type=int)

    limit = max(0, min(limit, 50))
    start = max(0, start)

    players = mdl_list_players(limit=limit, start=start)
    player_objects = []

    if players != None:
        for p in players:
            player_objects.append(p.get_object())

    return make_response(jsonify(player_objects), 200)


@players_index.route("/search")
def find_player():
    playerid = request.args.get("playerid", default=None, type=int)
    steamid = request.args.get("steamid", default=None, type=str)
    name = request.args.get("name", default=None, type=str)

    player = None

    if playerid != None:
        player = mdl_find_player(playerid=playerid)

    elif steamid != None:
        player = mdl_find_player(steamid=steamid)

    elif name != None:
        player = mdl_find_player(name=name)

    if player != None:
        player_object = player.get_object()
        return make_response(jsonify(player_object), 200)

    return make_response("", 204)
