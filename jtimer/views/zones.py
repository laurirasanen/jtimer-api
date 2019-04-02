"""flask views for /zones endpoint"""

from flask import jsonify, make_response, request
from flask_jwt_extended import jwt_required

from jtimer.blueprints import zones_index
from jtimer.models.database import Zone, Map, MapCheckpoint


@zones_index.route("/map/<int:map_id>", methods=["GET"])
def get_map_zones(map_id):
    """Get map zones.

    .. :quickref: Zones; Get map zones.

    **Example request**:

    .. sourcecode:: http

      GET /zones/map/1 HTTP/1.1

    **Example response**:

    .. sourcecode:: json

      [
          {
            "id": 1,
            "p1": [0, 0, 0],
            "p2": [256, 256, 256],
            "zone_type": "start"
          },
          {
            "id": 2,
            "p1": [1000, 1000, 1000],
            "p2": [1256, 1256, 1256],
            "zone_type": "end"
          },
          {
            "id": 1,
            "zone_type": "cp",
            "map_id": 1,
            "cp_index": 1,
            "zone": {
                "id": 3,
                "p1": [500, 500, 500],
                "p2": [756, 756, 756]
            }
          }
      ]

    :query map_id: map id.

    :status 200: Success.
    :status 404: Map not found.

    :returns: List of zones
    """

    map_ = Map.query.filter_by(id_=map_id).first()
    if map_ is None:
        error = {"message": "Map not found."}
        return make_response(jsonify(error), 404)

    zones = []
    if map_.start_zone is not None:
        zone = Zone.query.filter_by(id_=map_.start_zone).first()

        if zone:
            zone_dict = zone.json
            zone_dict["zone_type"] = "start"
            zones.append(zone_dict)

    if map_.end_zone is not None:
        zone = Zone.query.filter_by(id_=map_.end_zone).first()
        if zone:
            zone_dict = zone.json
            zone_dict["zone_type"] = "end"
            zones.append(zone_dict)

    checkpoints = MapCheckpoint.query.filter_by(map_id=map_id).all()
    if checkpoints:
        for checkpoint in checkpoints:
            zones.append(checkpoint.json)

    return make_response(jsonify(zones), 200)


@zones_index.route("/add/map/<int:map_id>", methods=["POST"])
@jwt_required
def add_map_zone(map_id):
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
    :query orientation: rotation around z-axis, used for start zones. (optional, default: 0)

    :status 200: Success.
    :status 404: Map not found.
    :status 415: Missing 'Content-Type: application/json' header.
    :status 422: Missing or invalid json content.

    :returns: Zone add result
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
    point1 = data.get("p1")
    if not isinstance(point1, list):
        error = {"message": "p1 is not type of list."}
        return make_response(jsonify(error), 422)

    if len(point1) != 3:
        error = {"message": "Length of p1 is not 3."}
        return make_response(jsonify(error), 422)

    for i in range(0, len(point1)):
        if not isinstance(point1[i], int):
            error = {"message": f"p1[{i}] is not type of int."}
            return make_response(jsonify(error), 422)

    # p2 validation
    point2 = data.get("p2")
    if not isinstance(point2, list):
        error = {"message": "p2 is not type of list."}
        return make_response(jsonify(error), 422)

    if len(point2) != 3:
        error = {"message": "Length of p2 is not 3."}
        return make_response(jsonify(error), 422)

    for i in range(0, len(point2)):
        if not isinstance(point2[i], int):
            error = {"message": f"p2[{i}] is not type of int."}
            return make_response(jsonify(error), 422)

    if zone_type == "start":
        # optional orientation
        orientation = data.get("orientation")
        if orientation:
            if not isinstance(orientation, int):
                error = {"message": "orientation is not type of int"}
                return make_response(jsonify(error), 422)

        # check for existing start zone
        zone = Zone.query.filter(Zone.id_ == map_.start_zone).first()
        if zone is None:
            zone = Zone()

        zone.x1, zone.y1, zone.z1 = point1
        zone.x2, zone.y2, zone.z2 = point2

        if orientation:
            zone.orientation = orientation

        zone.add()
        map_.start_zone = zone.id_
        map_.add()

    elif zone_type == "end":
        # check for existing end zone
        zone = Zone.query.filter(Zone.id_ == map_.end_zone).first()
        if zone is None:
            zone = Zone()

        zone.x1, zone.y1, zone.z1 = point1
        zone.x2, zone.y2, zone.z2 = point2

        zone.add()
        map_.end_zone = zone.id_
        map_.add()

    else:
        # checkpoints require index
        index = data.get("index")
        if index is None:
            error = {"message": "Missing index for zone_type 'cp'."}
            return make_response(jsonify(error), 422)

        # check for existing checkpoint
        checkpoint = MapCheckpoint.query.filter(
            MapCheckpoint.map_id == map_id, MapCheckpoint.cp_index == index
        ).first()

        if checkpoint is None:
            zone = Zone(
                x1=point1[0],
                y1=point1[1],
                z1=point1[2],
                x2=point2[0],
                y2=point2[1],
                z2=point2[2],
            )

            zone.add()

            checkpoint = MapCheckpoint(map_id=map_id, zone_id=zone.id_, cp_index=index)
        else:
            # check for existing zone
            zone = Zone.query.filter_by(id_=checkpoint.zone_id).first()

            if zone is None:
                zone = Zone()

            zone.x1, zone.y1, zone.z1 = point1
            zone.x2, zone.y2, zone.z2 = point2

            zone.add()

        checkpoint.add()

    response = {"message": "zone added."}
    return make_response(jsonify(response), 200)
