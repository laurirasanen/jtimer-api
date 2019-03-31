from flask import jsonify, make_response, request
from jtimer.blueprints import maps_index
from jtimer.extensions import db
from jtimer.models.database import Map, Author
from flask_jwt_extended import jwt_required, jwt_refresh_token_required


maps_index.route("/<int:id>/info", methods=["GET"])


def map_info(mapid):
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
    
    :query id: map id.
    
    :status 200: Success.
    :status 404: Map not found.
    :returns: Map info
    """
    m = Map.query.filter_by(mapid=mapid).first()
    authors = Author.query.filter_by(mapid=mapid).all()

    if m is None:
        response = {"message": "Map not found."}
        return make_response(jsonify(response), 404)

    response = m.serialize()
    response["authors"] = []
    if authors is not None:
        for a in authors:
            response["authors"].append(a.serialize())

    return make_response(jsonify(response), 200)
