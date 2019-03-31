from flask import jsonify, make_response, request, current_app
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    jwt_refresh_token_required,
    get_jwt_identity,
    get_raw_jwt,
)
from jtimer.blueprints import token_index
from jtimer.extensions import db
from jtimer.models.database import User, RevokedToken


@token_index.route("/auth", methods=["POST"])
def token_auth():
    """Get access and refresh tokens with user credentials.
    This should only be used for the initial authentication.
    Afterwards new access tokens can be requested using the refresh token and a seperate endpoint.

    .. :quickref: Token; Get access and refresh tokens.

    **Example request**:

    .. sourcecode:: http   
    
      POST /token/auth HTTP/1.1
      Content-Type: application/json
      { 
          "username": "Jane", 
          "password": "Doe" 
      }
    
    **Example response**:

    .. sourcecode:: json
    
      {
          "message": "Authenticated",
          "access_token": <access_token>,
          "access_token_expires_in": 3600,
          "refresh_token": <refresh_token>,
          "refresh_token_expires_in": 86400
      }
    
    :query username: username.
    :query password: password.
    
    :status 200: Authenticated.
    :status 401: Invalid username or password.
    :status 415: Missing 'Content-Type: application/json' header.
    :status 422: Missing json content.
    :returns: Refresh token, access token, expiry times
    """

    if not request.is_json:
        error = {"message": "Missing 'Content-Type: application/json' header."}
        return make_response(jsonify(error), 415)

    data = request.get_json()

    if data is None:
        error = {"message": "Missing json content"}
        return make_response(jsonify(error), 422)

    username = None
    if "username" in data.keys():
        username = data["username"]
    else:
        error = {"message": "Missing username"}
        return make_response(jsonify(error), 422)

    password = None
    if "password" in data.keys():
        password = data["password"]
    else:
        error = {"message": "Missing password"}
        return make_response(jsonify(error), 422)

    user = User.query.filter_by(username=username).first()

    if user:
        if user.verify_hash(password):
            refresh_token = create_refresh_token(identity=username)
            refresh_token_expires_in = current_app.config["JWT_REFRESH_TOKEN_EXPIRES"]
            access_token = create_access_token(identity=username)
            access_token_expires_in = current_app.config["JWT_ACCESS_TOKEN_EXPIRES"]

            response = {
                "message": "Authenticated",
                "refresh_token": refresh_token,
                "refresh_token_expires_in": refresh_token_expires_in,
                "access_token": access_token,
                "access_token_expires_in": access_token_expires_in,
            }
            return make_response(jsonify(response), 200)

    """Send same error if username OR password is incorrect.
    Don't tell the requester which one."""
    error = {"message": "Invalid username or password"}
    return make_response(jsonify(error), 401)


@token_index.route("/refresh", methods=["POST"])
@jwt_refresh_token_required
def token_refresh():
    """Get new access token with refresh token.

    .. :quickref: Token; Get new access token with refresh token.

    **Example request**:

    .. sourcecode:: http
    
      POST /token/refresh HTTP/1.1
      Authorization: Bearer <refresh_token>
    
    **Example response**:

    .. sourcecode:: json
    
      {
          "message": "Access token refreshed",
          "access_token": <access_token>,
          "expires_in": 3600
      }
    
    :query refresh_token: A valid refresh token.
    
    :status 200: Success.
    :returns: Access token
    """

    user = get_jwt_identity()
    access_token = create_access_token(identity=user)
    expires_in = current_app.config["JWT_ACCESS_TOKEN_EXPIRES"]
    response = {
        "message": "Access token refreshed",
        "access_token": access_token,
        "expires_in": expires_in,
    }
    return make_response(jsonify(response), 200)


@token_index.route("/revoke/refresh", methods=["POST"])
@jwt_refresh_token_required
def token_revoke_refresh():
    """Revoke refresh token.

    .. :quickref: Token; Revoke refresh token.

    **Example request**:

    .. sourcecode:: http
    
      POST /token/revoke/refresh HTTP/1.1
      Authorization: Bearer <refresh_token>
    
    **Example response**:

    .. sourcecode:: json
    
      {
          "message": "Refresh token has been revoked."
      }
    
    :query refresh_token: A valid refresh token.
    
    :status 200: Success.
    """

    try:
        jti = get_raw_jwt()["jti"]
        revoked_token = RevokedToken(jti=jti)
        revoked_token.add()
        response = {"message": "Refresh token has been revoked."}
        return make_response(jsonify(response), 200)
    except:
        response = {"message": "Something went wrong."}
        return make_response(jsonify(response), 500)


@token_index.route("/revoke/access", methods=["POST"])
@jwt_required
def token_revoke_access():
    """Revoke access token.

    .. :quickref: Token; Revoke access token.

    **Example request**:

    .. sourcecode:: http
    
      POST /token/revoke/access HTTP/1.1
      Authorization: Bearer <access_token>
    
    **Example response**:

    .. sourcecode:: json
    
      {
          "message": "Access token has been revoked."
      }
    
    :query access_token: A valid access token.
    
    :status 200: Success.
    """

    try:
        jti = get_raw_jwt()["jti"]
        revoked_token = RevokedToken(jti=jti)
        revoked_token.add()
        response = {"message": "Access token has been revoked."}
        return make_response(jsonify(response), 200)
    except:
        response = {"message": "Something went wrong."}
        return make_response(jsonify(response), 500)
