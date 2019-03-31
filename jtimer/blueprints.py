from flask import Blueprint

view_root = "jtimer.views"


def factory(views_path, url_prefix):
    import_name = f"{view_root}.{views_path}"
    blueprint = Blueprint(views_path, import_name, url_prefix=url_prefix)
    return blueprint


application_index = factory("index", "/")
players_index = factory("players", "/players")
token_index = factory("token", "/token")
user_index = factory("user", "/user")
maps_index = factory("maps", "/maps")
times_index = factory("times", "/times")

all_blueprints = (
    application_index,
    players_index,
    token_index,
    user_index,
    maps_index,
    times_index,
)
