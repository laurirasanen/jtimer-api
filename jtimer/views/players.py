"""flask views for /players endpoint"""

from flask import jsonify, make_response, request
from flask_jwt_extended import jwt_required

from jtimer.blueprints import players_index
from jtimer.models.database import Player
from jtimer.validation import validate_json


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

    players = Player.query.filter(Player.id_ >= start).order_by(Player.id_)[:limit]

    if players is None:
        return make_response("", 204)

    return make_response(jsonify([p.json for p in players]), 200)


@players_index.route("/search")
def find_player():
    """Search for a player.

    .. :quickref: Player; Find a player.

    **Example request**:

    .. sourcecode:: http

      GET /players/search?player_id=1 HTTP/1.1

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

    :query player_id: the playerid to search for.
    :query steam_id: the steamid to search for.
    :query name: the name to search for.

    **Note**: If multiple parameters are supplied, only one of them will be used.
    Parameters are prioritized in the order: playerid > steamid > name.

    :status 200: player found.
    :status 204: no player found.
    :returns: Player
    """
    player_id = request.args.get("player_id", default=None, type=int)
    steam_id = request.args.get("steam_id", default=None, type=str)
    name = request.args.get("name", default=None, type=str)

    player = Player.query.filter_by(id_=player_id).first()
    if player is None:
        player = Player.query.filter_by(steam_id=steam_id).first()
    if player is None:
        player = Player.query.filter_by(username=name).first()

    if player is None:
        return make_response("", 204)

    return make_response(jsonify(player.json), 200)


@players_index.route("/add", methods=["POST"])
@validate_json(
    {
        "steam_id": {"type": "string", "maxlength": 20, "empty": False},
        "username": {"type": "string", "maxlength": 32, "empty": False},
        "country": {"type": "string", "minlength": 2, "maxlength": 2, "empty": False},
    }
)
@jwt_required
def add_player():
    """Add a new player or update an existing one.

    .. :quickref: Player; Add a player.

    **Example request**:

    .. sourcecode:: http

      GET /players/add HTTP/1.1
      Authorization: Bearer <access_token>
      Content-Type: application/json
      {
          "steam_id": "STEAM_1:1:50152141"
      }

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

    :query steam_id: the steamid to register or update.

    :status 200: player registered or updated.
    :returns: Player
    """

    data = request.get_json()
    steam_id = data.get("steam_id")
    username = data.get("username")
    country = data.get("country")

    player = Player.query.filter_by(steam_id=steam_id).first()
    if player is None:
        player = Player(steam_id=steam_id)

    # update username and country for existing players as well
    player.username = username
    player.country = country

    player.add()

    return make_response(jsonify(player.json), 200)
