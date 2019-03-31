from jtimer.extensions import db
from passlib.hash import bcrypt


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
            "rank_info": {"soldier_points": self.spoints, "demo_points": self.dpoints},
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
    scompletions = db.Column("scompletions", db.Integer, default=0, nullable=False)
    dcompletions = db.Column("dcompletions", db.Integer, default=0, nullable=False)
    startzone = db.Column("startzone", None, db.ForeignKey("zone.id"), nullable=False)
    endzone = db.Column("endzone", None, db.ForeignKey("zone.id"), nullable=False)

    @property
    def serialize(self):
        return {
            "id": self.mapid,
            "name": self.mapname,
            "tiers": {"soldier": self.stier, "demoman": self.dtier},
            "completions": {"soldier": self.scompletions, "demoman": self.dcompletions},
        }


class Author(db.Model):
    authorid = db.Column("id", db.Integer, primary_key=True)
    name = db.Column("name", db.String(32), nullable=False)
    playerid = db.Column("playerid", None, db.ForeignKey("player.id"), nullable=True)
    mapid = db.Column("mapid", None, db.ForeignKey("map.id"), nullable=False)

    @property
    def serialize(self):
        player = Player.query.filter_by(playerid=playerid).first()
        if player:
            player_json = player.serialize()
            del player_json["rank_info"]
            player_json["name"] = self.name
            return player_json
        else:
            return {"name": self.name}


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


class User(db.Model):
    """Model for authenticating restricted views"""

    userid = db.Column("id", db.Integer, primary_key=True)
    username = db.Column("username", db.String(64), nullable=False)
    password = db.Column("password", db.String(256), nullable=False)

    @staticmethod
    def generate_hash(password):
        return bcrypt.hash(password)

    def verify_hash(self, password):
        return bcrypt.verify(password, self.password)

    def change_hash(self, password):
        self.password = self.generate_hash(password)
        db.session.commit()

    def add(self):
        query = User.query.filter_by(username=self.username).first()
        if not bool(query):
            db.session.add(self)
            db.session.commit()


class RevokedToken(db.Model):
    """Model for storing revoked tokens"""

    tokenid = db.Column("tokenid", db.Integer, primary_key=True)
    jti = db.Column("jti", db.String(120), nullable=False)

    def add(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def is_jti_blacklisted(cls, jti):
        query = cls.query.filter_by(jti=jti).first()
        return bool(query)
