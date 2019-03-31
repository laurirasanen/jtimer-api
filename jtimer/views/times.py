from flask import jsonify, make_response, request
from jtimer.blueprints import times_index
from jtimer.extensions import db
from jtimer.models.database import MapTimes, Author
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
