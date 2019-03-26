import os
from sqlalchemy import (
    create_engine,
    Table,
    Column,
    Integer,
    String,
    MetaData,
    ForeignKey,
)
from sqlalchemy.engine.url import URL
from flask import current_app

db_url = URL(
    "mysql",
    username=current_app.config["MYSQL_USER"],
    password=current_app.config["MYSQL_PASSWORD"],
    host=current_app.config["MYSQL_HOST"],
    port=current_app.config["MYSQL_PORT"],
    database=current_app.config["MYSQL_DB"],
)
engine = create_engine(db_url)
metadata = MetaData(bind=engine)


class Tables:
    players = Table(
        "players",
        metadata,
        Column("id", Integer, primary_key=True),
        Column("steamid", String(17), nullable=False),
        Column("username", String(32), nullable=False),
        Column("country", String(2), nullable=False),
        Column("spoints", Integer, default=0, nullable=False),
        Column("dpoints", Integer, default=0, nullable=False),
    )

    zones = Table(
        "zones",
        metadata,
        Column("id", Integer, primary_key=True),
        Column("x1", Integer, nullable=False),
        Column("y1", Integer, nullable=False),
        Column("z1", Integer, nullable=False),
        Column("x2", Integer, nullable=False),
        Column("y2", Integer, nullable=False),
        Column("z2", Integer, nullable=False),
    )

    maps = Table(
        "maps",
        metadata,
        Column("id", Integer, primary_key=True),
        Column("mapname", String(128), nullable=False),
        Column("stier", Integer, default=0, nullable=False),
        Column("dtier", Integer, default=0, nullable=False),
        Column("completions", Integer, default=0, nullable=False),
        Column("startzone", None, ForeignKey("zones.id"), nullable=False),
        Column("endzone", None, ForeignKey("zones.id"), nullable=False),
    )

    authors = Table(
        "authors",
        metadata,
        Column("id", Integer, primary_key=True),
        Column("playerid", None, ForeignKey("players.id"), nullable=False),
        Column("mapidid", None, ForeignKey("maps.id"), nullable=False),
    )

    courses = Table(
        "courses",
        metadata,
        Column("id", Integer, primary_key=True),
        Column("mapid", None, ForeignKey("maps.id"), nullable=False),
        Column("courseindex", Integer, nullable=False),
        Column("stier", Integer, default=0, nullable=False),
        Column("dtier", Integer, default=0, nullable=False),
        Column("completions", Integer, default=0, nullable=False),
        Column("startzone", None, ForeignKey("zones.id"), nullable=False),
        Column("endzone", None, ForeignKey("zones.id"), nullable=False),
    )

    bonuses = Table(
        "bonuses",
        metadata,
        Column("id", Integer, primary_key=True),
        Column("mapid", None, ForeignKey("maps.id"), nullable=False),
        Column("bonusindex", Integer, nullable=False),
        Column("stier", Integer, default=0, nullable=False),
        Column("dtier", Integer, default=0, nullable=False),
        Column("completions", Integer, default=0, nullable=False),
        Column("startzone", None, ForeignKey("zones.id"), nullable=False),
        Column("endzone", None, ForeignKey("zones.id"), nullable=False),
    )

    mapcheckpoints = Table(
        "mapcheckpoints",
        metadata,
        Column("id", Integer, primary_key=True),
        Column("zoneid", None, ForeignKey("zones.id"), nullable=False),
        Column("mapid", None, ForeignKey("maps.id"), nullable=False),
        Column("cpindex", Integer, nullable=False),
    )

    coursecheckpoints = Table(
        "coursecheckpoints",
        metadata,
        Column("id", Integer, primary_key=True),
        Column("zoneid", None, ForeignKey("zones.id"), nullable=False),
        Column("courseid", None, ForeignKey("courses.id"), nullable=False),
        Column("cpindex", Integer, nullable=False),
    )

    bonuscheckpoints = Table(
        "bonuscheckpoints",
        metadata,
        Column("id", Integer, primary_key=True),
        Column("zoneid", None, ForeignKey("zones.id"), nullable=False),
        Column("bonusid", None, ForeignKey("bonuses.id"), nullable=False),
        Column("cpindex", Integer, nullable=False),
    )


# don't create tables if we're just building docs
if os.environ.get("READTHEDOCS") is not "True":
    metadata.create_all()
