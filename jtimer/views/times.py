from flask import jsonify, make_response, request
from jtimer.blueprints import times_index
from jtimer.extensions import db
from jtimer.models.database import MapTimes, Author
from flask_jwt_extended import jwt_required, jwt_refresh_token_required


@times_index.route("/maps/<int:mapid>", methods=["GET"])
def get_times(mapid):
    limit = request.args.get("limit", default=50, type=int)
    start = request.args.get("start", default=1, type=int)

    limit = max(1, min(limit, 50))
    start = max(1, start)

    times = (
        MapTimes.query.filter(MapTimes.id_ == mapid and MapTimes.rank >= start)
        .sort_by(rank)
        .all()[:limit]
    )

    if times is None:
        return make_response("", 204)
    else:
        return make_response(jsonify([t.serialize for t in times]), 200)
