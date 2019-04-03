"""flask views for /times endpoint"""

from flask import jsonify, make_response, request
from flask_jwt_extended import jwt_required

from jtimer.blueprints import times_index
from jtimer.models.database import Map, MapTimes, InsertResult
from jtimer.validation import validate_json


@times_index.route("/map/<int:map_id>", methods=["GET"])
def get_times(map_id):
    """Get map times with id.

    .. :quickref: Times; Get map times.

    **Example request**:

    .. sourcecode:: http

      POST /times/map/1?limit=1 HTTP/1.1

    **Example response**:

    .. sourcecode:: json

      [
          {
              "id": 56,
              "map_id": 1,
              "player": {
                  "id": 24,
                  "steamid": "STEAM:0:1:2001501",
                  "name": "Jane",
                  "country": "UK",
                  "rank_info": {
                      "soldier_points": 41004,
                      "demo_points": 10244,
                  }
              },
              "class": 2,
              "time": 10424.51525167,
              "rank": 1,
          }
      ]

    :query map_id: map id.

    :status 200: Success.
    :status 404: Map not found.
    :returns: Map info
    """
    limit = request.args.get("limit", default=50, type=int)
    start = request.args.get("start", default=1, type=int)

    limit = max(1, min(limit, 50))
    start = max(1, start)

    times = (
        MapTimes.query.filter(MapTimes.id_ == map_id, MapTimes.rank >= start)
        .order_by(MapTimes.rank)
        .all()[:limit]
    )

    if times is None:
        return make_response("", 204)

    return make_response(jsonify([t.json for t in times]), 200)


@times_index.route("/insert/map/<int:map_id>", methods=["POST"])
@validate_json(
    {
        "player_id": {"type": "integer", "min": 1, "required": True},
        "player_class": {"type": "integer", "allowed": [2, 4], "required": True},
        "start_time": {"type": "float", "min": 0, "required": True},
        "end_time": {"type": "float", "min": 0, "required": True},
    }
)
@jwt_required
def insert_map(map_id):
    """Insert run to map with id.

    .. :quickref: Times; Insert map time.

    **Example request**:

    .. sourcecode:: http

      POST /times/insert/map/1 HTTP/1.1
      Authorization: Bearer <access_token>
      {
          "player_id": 1,
          "player_class": 2,
          "start_time": 9876.54321,
          "end_time": 12345.6789
      }

    **Example response**:

    .. sourcecode:: json

      [
          {
              "result": 2,
              "rank": 9,
              "points_gained": 404,
              "completions": {
                  "soldier": 1000,
                  "demoman": 500
              },
              "records": {
                  "soldier": 1860.4123,
                  "demoman": 1752.5105
              },
              "duration": 2469.13569,
              "improvement": 1234.56789,
              "message": "Time updated."
          }
      ]

    :query map_id: map id.
    :query player_id: player id.
    :query player_class: player class.
    :query start_time: run start time.
    :query end_time: run end time.

    :status 200: Success.
    :status 404: Map not found.
    :status 415: Missing 'Content-Type: application/json' header.
    :status 422: Missing or invalid json content.
    :returns: Insert result
    """

    data = request.get_json()

    if map_id < 1:
        error = {"message": "map_id is invalid."}
        return make_response(jsonify(error), 422)

    player_id = data.get("player_id")
    player_class = data.get("player_class")
    start_time = data.get("start_time")
    end_time = data.get("end_time")

    if end_time < start_time:
        error = {"message": "end_time must be greater than start_time"}
        return make_response(jsonify(error), 422)

    map_ = Map.query.filter_by(id_=map_id).first()
    if map_ is None:
        error = {"message": f"Could not find map with id {map_id}."}
        return make_response(jsonify(error), 404)

    entry = MapTimes(
        map_id=map_id,
        player_id=player_id,
        player_class=player_class,
        start_time=start_time,
        end_time=end_time,
        duration=end_time - start_time,
    )
    response = entry.add()

    if response["result"] is InsertResult.ADDED:
        response["message"] = "Time added."

    elif response["result"] is InsertResult.UPDATED:
        response["message"] = "Time updated."

    else:
        response["message"] = "Slower than PR, no update."

    response["result"] = int(response["result"])

    return make_response(jsonify(response), 200)
