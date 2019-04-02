"""flask views for /maps endpoint"""

from flask import jsonify, make_response, request
from flask_jwt_extended import jwt_required

from jtimer.blueprints import maps_index
from jtimer.models.database import Map, Author
from jtimer.validation import validate_json


@maps_index.route("/<int:map_id>/info", methods=["GET"])
def map_info(map_id):
    """Get map info with id.

    .. :quickref: Maps; Get map info.

    **Example request**:

    .. sourcecode:: http

      POST /maps/1/info HTTP/1.1

    **Example response**:

    .. sourcecode:: json

      {
          "id": 1,
          "name": "jump_soar_a4",
          "tiers": {
              "soldier": 5,
              "demoman": 3
          },
          "completions": {
              "soldier": 1402,
              "demoman": 2401
          },
          "authors": [
              {
                  "id": 5,
                  "name": "Matti",
                  "country": "UK"
              }
          ]
      }

    :query map_id: map id.

    :status 200: Success.
    :status 404: Map not found.
    :returns: Map info
    """
    map_ = Map.query.filter_by(id_=map_id).first()
    authors = Author.query.filter_by(id_=map_id).all()

    if map_ is None:
        response = {"message": "Map not found."}
        return make_response(jsonify(response), 404)

    response = map_.json
    response["authors"] = []
    if authors is not None:
        for author in authors:
            response["authors"].append(author.json)

    return make_response(jsonify(response), 200)


@maps_index.route("/name/<string:mapname>", methods=["GET"])
def map_info_name(mapname):
    """Get map by name.

    .. :quickref: Maps; Get map by name.

    **Example request**:

    .. sourcecode:: http

      POST /maps/name/jump_soar_a4 HTTP/1.1

    **Example response**:

    .. sourcecode:: json

      {
          "id": 1,
          "name": "jump_soar_a4",
          "tiers": {
              "soldier": 5,
              "demoman": 3
          },
          "completions": {
              "soldier": 1402,
              "demoman": 2401
          },
          "authors": [
              {
                  "id": 5,
                  "name": "Matti",
                  "country": "UK"
              }
          ]
      }

    :query mapname: map name.

    :status 200: Success.
    :status 404: Map not found.
    :returns: Map info
    """
    map_ = Map.query.filter_by(mapname=mapname).first()

    if map_ is None:
        response = {"message": "Map not found."}
        return make_response(jsonify(response), 404)

    authors = Author.query.filter_by(id_=map_.id_).all()

    response = map_.json
    response["authors"] = []
    if authors is not None:
        for author in authors:
            response["authors"].append(author.json)

    return make_response(jsonify(response), 200)


@maps_index.route("/add", methods=["POST"])
@jwt_required
def add_map():
    """Add a new map.

    .. :quickref: Maps; Add a new map.

    **Example request**:

    .. sourcecode:: http

      POST /maps/add HTTP/1.1
      Authorization: Bearer <access_token>
      {
          "name": "jump_soar_a4"
      }

    **Example response**:

    .. sourcecode:: json

      {
          "message": "map 'jump_soar_a4' added!",
          "map_id": 1
      }

    :query name: map name.
    :query stier: soldier tier. (default: 0, min: 0, max: 10)
    :query dtier: demoman tier. (default: 0, min: 0, max: 10)

    :status 200: Success.
    :status 409: Map name already exists.
    :status 415: Missing 'Content-Type: application/json' header.
    :status 422: Missing or invalid json content.

    :returns: Map added result.
    """

    if not request.is_json:
        error = {"message": "Missing 'Content-Type: application/json' header."}
        return make_response(jsonify(error), 415)

    data = request.get_json()

    if data is None:
        error = {"message": "Missing json content"}
        return make_response(jsonify(error), 422)

    # name validation
    name = data.get("name")
    if name is None:
        error = {"message": "Missing name."}
        return make_response(jsonify(error), 422)

    if not isinstance(name, str):
        error = {"message": "name is not type of str."}
        return make_response(jsonify(error), 422)

    if len(name) > 128:
        error = {"message": "name is too long. Max length: 128."}
        return make_response(jsonify(error), 422)

    # stier validation
    stier = data.get("stier")
    if stier is not None:
        if not isinstance(stier, int):
            error = {"message": "stier is not type of int."}
            return make_response(jsonify(error), 422)

        if stier < 0:
            error = {"message": "stier is negative."}
            return make_response(jsonify(error), 422)

        if stier > 10:
            error = {"message": "stier is too big. Max value: 10"}
            return make_response(jsonify(error), 422)
    else:
        stier = 0

    # dtier validation
    dtier = data.get("dtier")
    if dtier is not None:
        if not isinstance(dtier, int):
            error = {"message": "dtier is not type of int."}
            return make_response(jsonify(error), 422)

        if dtier < 0:
            error = {"message": "dtier is negative."}
            return make_response(jsonify(error), 422)

        if dtier > 10:
            error = {"message": "dtier is too big.  Max value: 10"}
            return make_response(jsonify(error), 422)
    else:
        dtier = 0

    query = Map.query.filter_by(mapname=name).first()
    if query:
        error = {
            "message": f"map with name '{name}' already exists (id: {query.id_})! Use update endpoint instead."
        }
        return make_response(jsonify(error), 409)

    map_ = Map(mapname=name, stier=stier, dtier=dtier)
    map_.add()
    response = {"message": f"map '{name}' added!", "map_id": map_.id_}
    return make_response(jsonify(response), 200)


@maps_index.route("/update/<int:map_id>", methods=["POST"])
@validate_json(
    {
        "name": {"type": "string", "maxlength": 128, "required": False},
        "stier": {"type": "integer", "min": 0, "max": 10, "required": False},
        "dtier": {"type": "integer", "min": 0, "max": 10, "required": False},
    }
)
@jwt_required
def update(map_id):
    """Update existing map.

    .. :quickref: Maps; Update existing map.

    **Example request**:

    .. sourcecode:: http

      POST /maps/update/1 HTTP/1.1
      Authorization: Bearer <access_token>
      {
          "stier": 10
      }

    **Example response**:

    .. sourcecode:: json

      {
          "message": "map updated!",
          "map_id": 1,
          "name": "jump_soar_a4",
          "stier": 10,
          "dtier": 3
      }

    :query name: map name. (optional, max length: 128)
    :query stier: soldier tier. (optional, min: 0, max: 10)
    :query dtier: demoman tier. (optional, min: 0, max: 10)

    :status 200: Success.
    :status 409: Map name already exists.
    :status 415: Missing 'Content-Type: application/json' header.
    :status 422: Missing or invalid json content.

    :returns: Map added result.
    """

    data = request.get_json()

    map_ = Map.query.filter_by(id_=map_id).first()

    if map_ is None:
        response = {"message": "Map not found."}
        return make_response(jsonify(response), 404)

    if "stier" is not data.keys():
        map_.stier = data["stier"]

    if "dtier" in data.keys():
        map_.dtier = data["dtier"]

    # check if updated name is already taken
    if "name" in data.keys():
        query = Map.query.filter_by(mapname=data["name"]).first()
        if query:
            error = {"message": f"map with name '{data['name']}' already exists!"}
            return make_response(jsonify(error), 409)

        map_.mapname = data["name"]

    map_.add()
    response = {
        "message": "map updated!",
        "map_id": map_.id_,
        "name": map_.mapname,
        "stier": map_.stier,
        "dtier": map_.dtier,
    }
    return make_response(jsonify(response), 200)
