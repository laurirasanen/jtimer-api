from jtimer.extensions import db


class Player(db.Model):
    playerid = db.Column("id", db.Integer, primary_key=True)
    steamid = db.Column("steamid", db.String(17), nullable=False)
    username = db.Column("username", db.String(32), nullable=False)
    country = db.Column("country", db.String(2), nullable=False)
    spoints = db.Column("spoints", db.Integer, default=0, nullable=False)
    dpoints = db.Column("dpoints", db.Integer, default=0, nullable=False)

    @property
    def serialize(self):
        return {
            "id": self.playerid,
            "steamid": self.steamid,
            "name": self.username,
            "country": self.country,
            "rank_info": {
                "spoints": self.spoints,
                "dpoints": self.dpoints
            }
        }
    


class Zone(db.Model):
    zoneid = db.Column("id", db.Integer, primary_key=True)
    x1 = db.Column("x1", db.Integer, nullable=False)
    y1 = db.Column("y1", db.Integer, nullable=False)
    z1 = db.Column("z1", db.Integer, nullable=False)
    x2 = db.Column("x2", db.Integer, nullable=False)
    y2 = db.Column("y2", db.Integer, nullable=False)
    z2 = db.Column("z2", db.Integer, nullable=False)


class Map(db.Model):
    mapid = db.Column("id", db.Integer, primary_key=True)
    mapname = db.Column("mapname", db.String(128), nullable=False)
    stier = db.Column("stier", db.Integer, default=0, nullable=False)
    dtier = db.Column("dtier", db.Integer, default=0, nullable=False)
    completions = db.Column("completions", db.Integer, default=0, nullable=False)
    startzone = db.Column("startzone", None, db.ForeignKey("zone.id"), nullable=False)
    endzone = db.Column("endzone", None, db.ForeignKey("zone.id"), nullable=False)


class Author(db.Model):
    authorid = db.Column("id", db.Integer, primary_key=True)
    playerid = db.Column("playerid", None, db.ForeignKey("player.id"), nullable=False)
    mapid = db.Column("mapid", None, db.ForeignKey("map.id"), nullable=False)


class Course(db.Model):
    courseid = db.Column("id", db.Integer, primary_key=True)
    mapid = db.Column("mapid", None, db.ForeignKey("map.id"), nullable=False)
    courseindex = db.Column("courseindex", db.Integer, nullable=False)
    stier = db.Column("stier", db.Integer, default=0, nullable=False)
    dtier = db.Column("dtier", db.Integer, default=0, nullable=False)
    completions = db.Column("completions", db.Integer, default=0, nullable=False)
    startzone = db.Column("startzone", None, db.ForeignKey("zone.id"), nullable=False)
    endzone = db.Column("endzone", None, db.ForeignKey("zone.id"), nullable=False)


class Bonus(db.Model):
    bonusid = db.Column("id", db.Integer, primary_key=True)
    mapid = db.Column("mapid", None, db.ForeignKey("map.id"), nullable=False)
    bonusindex = db.Column("bonusindex", db.Integer, nullable=False)
    stier = db.Column("stier", db.Integer, default=0, nullable=False)
    dtier = db.Column("dtier", db.Integer, default=0, nullable=False)
    completions = db.Column("completions", db.Integer, default=0, nullable=False)
    startzone = db.Column("startzone", None, db.ForeignKey("zone.id"), nullable=False)
    endzone = db.Column("endzone", None, db.ForeignKey("zone.id"), nullable=False)


class MapCheckpoint(db.Model):
    checkpointid = db.Column("id", db.Integer, primary_key=True)
    zoneid = db.Column("zoneid", None, db.ForeignKey("zone.id"), nullable=False)
    mapid = db.Column("mapid", None, db.ForeignKey("map.id"), nullable=False)
    cpindex = db.Column("cpindex", db.Integer, nullable=False)


class CourseCheckpoint(db.Model):
    checkpointid = db.Column("id", db.Integer, primary_key=True)
    zoneid = db.Column("zoneid", None, db.ForeignKey("zone.id"), nullable=False)
    courseid = db.Column("courseid", None, db.ForeignKey("course.id"), nullable=False)
    cpindex = db.Column("cpindex", db.Integer, nullable=False)


class BonusCheckpoint(db.Model):
    checkpointid = db.Column("id", db.Integer, primary_key=True)
    zoneid = db.Column("zoneid", None, db.ForeignKey("zone.id"), nullable=False)
    bonusid = db.Column("bonusid", None, db.ForeignKey("bonus.id"), nullable=False)
    cpindex = db.Column("cpindex", db.Integer, nullable=False)
