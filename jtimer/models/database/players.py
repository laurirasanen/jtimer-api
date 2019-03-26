from . import engine
from . import Tables


def list_players(start=0, limit=50):
    result = []
    with engine.begin() as conn:
        result = (
            Tables.players.select()
            .where(Tables.players.c.id >= start)
            .order_by(Tables.players.c.id)
            .execute()
        )

    return result


def find_player(playerid=None, steamid=None, name=None):
    result = []

    if playerid != None:
        result = (
            Tables.players.select().where(Tables.players.c.id == playerid).execute()
        )

    elif steamid != None:
        result = (
            Tables.players.select().where(Tables.players.c.steamid == steamid).execute()
        )

    elif name != None:
        result = (
            Tables.players.select().where(Tables.players.c.username == name).execute()
        )

    return result
