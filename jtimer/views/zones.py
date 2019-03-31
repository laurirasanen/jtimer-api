from flask import jsonify, make_response, request
from jtimer.blueprints import zones_index
from jtimer.extensions import db
from jtimer.models.database import Zone, Map, MapCheckpoint
from flask_jwt_extended import jwt_required


@zones_index.route("/add/map/<int:map_id>", methods=["POST"])
@jwt_required
def add_map_zone():
    """Add zone to a map.

    .. :quickref: Zones; Add zone to a map.

    **Example request**:

    .. sourcecode:: http

      POST /zones/add/map/1 HTTP/1.1
      Authorization: Bearer <access_token>
      {
          "zone_type": "start",
          "p1": [0, 256, 128],
          "p2": [256, 0, 256]
      }
    
    **Example response**:

    .. sourcecode:: json

      {
          "message": "zone added."
      }
    
    :query map_id: map id.
    :query zone_type: type of zone. ("start", "end", "cp")
    :query p1: first corner of the zone. (list of integers)
    :query p2: second corner of the zone. (list of integers)
    :query index: checkpoint index. (required if zone_type="cp")
    
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

    # make sure map exists
    map_ = Map.query.filter_by(id_=map_id).first()
    if map_ is None:
        error = {"message": "Map not found."}
        return make_response(jsonify(error), 404)

    # zone_type validation
    zone_type = data.get("zone_type")
    if zone_type is None:
        error = {"message": "Missing zone_type argument."}
        return make_response(jsonify(error), 422)

    if not isinstance(zone_type, str):
        error = {"message": "zone_type is not type(str)."}
        return make_response(jsonify(error), 422)

    if zone_type not in ["start", "end", "cp"]:
        error = {
            "message": "zone_type is not valid. Acceptable types: 'start', 'end', 'cp'."
        }
        return make_response(jsonify(error), 422)

    # p1 validation
    p1 = data.get("p1")
    if not isinstance(p1, list):
        error = {"message": "p1 is not type of list."}
        return make_response(jsonify(error), 422)

    if len(p1) != 3:
        error = {"message": "Length of p1 is not 3."}
        return make_response(jsonify(error), 422)

    for i in range(0, len(p1)):
        if not isinstance(p1[i], int):
            error = {"message": f"p1[{i}] is not type of int."}
            return make_response(jsonify(error), 422)

    # p2 validation
    p2 = data.get("p2")
    if not isinstance(p2, list):
        error = {"message": "p2 is not type of list."}
        return make_response(jsonify(error), 422)

    if len(p2) != 3:
        error = {"message": "Length of p2 is not 3."}
        return make_response(jsonify(error), 422)

    for i in range(0, len(p2)):
        if not isinstance(p2[i], int):
            error = {"message": f"p2[{i}] is not type of int."}
            return make_response(jsonify(error), 422)

    if zone_type == "start":
        # check for existing start zone
        zone = Zone.query.filter(
            Zone.map_id == map_id and Zone.id_ == map_.start_zone
        ).first()
        if zone is None:
            zone = Zone(x1=p1[0], y1=p1[1], z1=p1[2], x2=p2[0], y2=p2[1], z2=p2[2])
        zone.add()
        map_.start_zone = zone.id_
        map_.add()

    elif zone_type == "end":
        # check for existing end zone
        zone = Zone.query.filter(
            Zone.map_id == map_id and Zone.id_ == map_.end_zone
        ).first()
        if zone is None:
            zone = Zone(x1=p1[0], y1=p1[1], z1=p1[2], x2=p2[0], y2=p2[1], z2=p2[2])
        zone.add()
        map_.end_zone = zone.id_
        map_.add()

    else:
        # checkpoints require index
        index = data.get("index")
        if index is None:
            error = {"message": "Missing index for zone_type 'cp'."}
            return make_response(jsonify(error), 422)

        zone = Zone(x1=p1[0], y1=p1[1], z1=p1[2], x2=p2[0], y2=p2[1], z2=p2[2])
        zone.add()
        cp = MapCheckpoint(map_id=map_id, zone_id=zone.id_, cp_index=index)
        cp.add()

    response = {"message": "zone added."}
    make_response(jsonify(response), 200)
