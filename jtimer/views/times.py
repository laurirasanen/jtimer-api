from flask import jsonify, make_response, request
from jtimer.blueprints import times_index
from jtimer.extensions import db
from jtimer.models.database import Map, MapTimes, Author, InsertResult
from flask_jwt_extended import jwt_required, jwt_refresh_token_required


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
        MapTimes.query.filter(MapTimes.id_ == map_id and MapTimes.rank >= start)
        .order_by(MapTimes.rank)
        .all()[:limit]
    )

    if times is None:
        return make_response("", 204)
    else:
        return make_response(jsonify([t.serialize for t in times]), 200)


@times_index.route("/insert/map/<int:map_id>")
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
          "start_time": 12345.6789,
          "end_time": 9876.54321
      }
    
    **Example response**:

    .. sourcecode:: json

      [
          {
              "result": 2,
              "rank": 9,
              "points_gained": 404,
              "completions": 1025,
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
    if not request.is_json:
        error = {"message": "Missing 'Content-Type: application/json' header."}
        return make_response(jsonify(error), 415)

    data = request.get_json()

    if data is None:
        error = {"message": "Missing json content"}
        return make_response(jsonify(error), 422)

    # map_id validation
    if map_id < 1:
        error = {"message": "map_id is invalid."}
        return make_response(jsonify(error), 422)

    # player_id validation
    player_id = data.get("player_id")
    if player_id is None:
        error = {"message": "Missing player_id"}
        return make_response(jsonify(error), 422)

    if not isinstance(player_id, int):
        error = {"message": "player_id is not type of int."}
        return make_response(jsonify(error), 422)

    if player_id < 1:
        error = {"message": f"player_id value of {player_id} is invalid."}
        return make_response(jsonify(error), 422)

    # player class validation
    player_class = data.get("player_class")
    if player_class is None:
        error = {"message": "Missing player_class"}
        return make_response(jsonify(error), 422)

    if not isinstance(player_class, int):
        error = {"message": "player_class is not type of int."}
        return make_response(jsonify(error), 422)

    if player_class != 2 and player_class != 4:
        error = {
            "message": f"player_class value of {player_class} is invalid. Value of 2 or 4 required."
        }
        return make_response(jsonify(error), 422)

    # start_time validation
    start_time = data.get("start_time")
    if start_time is None:
        error = {"message": "Missing start_time"}
        return make_response(jsonify(error), 422)

    if not isinstance(start_time, float):
        error = {"message": "start_time is not type of float."}
        return make_response(jsonify(error), 422)

    if start_time < 0:
        error = {"message": "start_time is negative."}
        return make_response(jsonify(error), 422)

    # end_time validation
    end_time = data.get("end_time")
    if end_time is None:
        error = {"message": "Missing end_time"}
        return make_response(jsonify(error), 422)

    if not isinstance(end_time, float):
        error = {"message": "end_time is not type of float."}
        return make_response(jsonify(error), 422)

    if end_time < 0:
        error = {"message": "end_time is negative."}
        return make_response(jsonify(error), 422)

    map_ = Map.query.filter_by(id_=map_id).first()
    if map_ is None:
        error = {"message": f"Could not find map with id {map_id}."}
        return make_response(jsonify(error), 404)

    entry = MapTimes(
        map_id=map_id, player_id=player_id, start_time=start_time, end_time=end_time
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
