from flask import jsonify, make_response, request
from jtimer.blueprints import players_index
from jtimer.extensions import db
from jtimer.models.database import Player


@players_index.route("/list")
def list_players():
    """Return a list of players.

    .. :quickref: Player; Get a list of players.

    **Example request**:

    .. sourcecode:: http

      GET /players/list?limit=2 HTTP/1.1

    **Example response**:

    .. sourcecode:: json
    
      [
          {
              "id": 1,
              "name": "Larry",
              "rank_info": {
                  "demo_points": 0,
                  "demo_rank": 0,
                  "soldier_points": 0,
                  "soldier_rank": 0
              },
              "steamid": "STEAM_1:1:50152141"
          },
          {
              "id": 2,
              "name": "kaptain",
              "rank_info": {
                  "demo_points": 0,
                  "demo_rank": 0,
                  "soldier_points": 0,
                  "soldier_rank": 0
              },
              "steamid": "STEAM_0:0:36730682"
          }
      ]
    
    :query limit: amount of players to get. (default: 50, min: 1, max: 50)
    :query start: player id to start the list from. (default: 1, min: 1)
    :status 200: players found.
    :returns: Player
    """
    limit = request.args.get("limit", default=50, type=int)
    start = request.args.get("start", default=1, type=int)

    limit = max(1, min(limit, 50))
    start = max(1, start)

    players = Player.query.filter(Player.playerid >= start).order_by(Player.playerid)[
        :limit
    ]

    if players is None:
        return make_response("", 204)
    else:
        return make_response(jsonify([p.serialize for p in players]), 200)


@players_index.route("/search")
def find_player():
    """Search for a player.

    .. :quickref: Player; Find a player.

    **Example request**:

    .. sourcecode:: http
    
      GET /players/search?playerid=1 HTTP/1.1
    
    **Example response**:

    .. sourcecode:: json
    
      {
          "id": 1,
          "name": "Larry",
          "rank_info": {
              "demo_points": 0,
              "demo_rank": 0,
              "soldier_points": 0,
              "soldier_rank": 0
          },
          "steamid": "STEAM_1:1:50152141"
      }
    
    :query playerid: the playerid to search for.
    :query steamid: the steamid to search for.
    :query name: the name to search for.

    **Note**: If multiple parameters are supplied, only one of them will be used.
    Parameters are prioritized in the order: playerid > steamid > name.
    
    :status 200: player found.
    :status 204: no player found.
    :returns: Player
    """
    playerid = request.args.get("playerid", default=None, type=int)
    steamid = request.args.get("steamid", default=None, type=str)
    name = request.args.get("name", default=None, type=str)

    player = Player.query.filter_by(playerid=playerid).first()
    if player is None:
        player = Player.query.filter_by(steamid=steamid).first()
    if player is None:
        player = Player.query.filter_by(username=name).first()

    if player is None:
        return make_response("", 204)
    else:
        return make_response(jsonify(player.serialize), 200)
