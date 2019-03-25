from flask import Blueprint

view_root = "jtimer.views"


def factory(views_path, url_prefix):
    import_name = f"{view_root}.{views_path}"
    blueprint = Blueprint(views_path, import_name, url_prefix=url_prefix)
    return blueprint


application_index = factory("index", "/")
players_index = factory("players", "/players")

all_blueprints = (application_index, players_index)
