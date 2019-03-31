from jtimer.extensions import db
from passlib.hash import bcrypt


class Player(db.Model):
    id_ = db.Column("id", db.Integer, primary_key=True)
    steam_id = db.Column(db.String(17), nullable=False)
    username = db.Column(db.String(32), nullable=False)
    country = db.Column(db.String(2), nullable=False)
    s_points = db.Column(db.Integer, default=0, nullable=False)
    d_points = db.Column(db.Integer, default=0, nullable=False)

    @property
    def serialize(self):
        return {
            "id": self.id_,
            "steamid": self.steamid,
            "name": self.username,
            "country": self.country,
            "rank_info": {
                "soldier_points": self.s_points,
                "demo_points": self.d_points,
            },
        }


class Zone(db.Model):
    id_ = db.Column("id", db.Integer, primary_key=True)
    x1 = db.Column(db.Integer, nullable=False)
    y1 = db.Column(db.Integer, nullable=False)
    z1 = db.Column(db.Integer, nullable=False)
    x2 = db.Column(db.Integer, nullable=False)
    y2 = db.Column(db.Integer, nullable=False)
    z2 = db.Column(db.Integer, nullable=False)


class Map(db.Model):
    id_ = db.Column("id", db.Integer, primary_key=True)
    mapname = db.Column(db.String(128), nullable=False)
    stier = db.Column(db.Integer, default=0, nullable=False)
    dtier = db.Column(db.Integer, default=0, nullable=False)
    s_completions = db.Column(db.Integer, default=0, nullable=False)
    d_completions = db.Column(db.Integer, default=0, nullable=False)
    start_zone = db.Column(None, db.ForeignKey("zone.id"), nullable=False)
    end_zone = db.Column(None, db.ForeignKey("zone.id"), nullable=False)

    @property
    def serialize(self):
        return {
            "id": self.id_,
            "name": self.mapname,
            "tiers": {"soldier": self.stier, "demoman": self.dtier},
            "completions": {
                "soldier": self.s_completions,
                "demoman": self.d_completions,
            },
        }


class Author(db.Model):
    id_ = db.Column("id", db.Integer, primary_key=True)
    name = db.Column(db.String(32), nullable=False)
    player_id = db.Column(None, db.ForeignKey("player.id"), nullable=True)
    map_id = db.Column(None, db.ForeignKey("map.id"), nullable=False)

    @property
    def serialize(self):
        player = Player.query.filter_by(playerid=playerid).first()
        if player:
            player_dict = player.serialize()
            del player_dict["rank_info"]
            player_dict["name"] = self.name
            return player_dict
        else:
            return {"name": self.name}


class Course(db.Model):
    id_ = db.Column("id", db.Integer, primary_key=True)
    map_id = db.Column(None, db.ForeignKey("map.id"), nullable=False)
    course_index = db.Column(db.Integer, nullable=False)
    stier = db.Column(db.Integer, default=0, nullable=False)
    dtier = db.Column(db.Integer, default=0, nullable=False)
    s_completions = db.Column(db.Integer, default=0, nullable=False)
    d_completions = db.Column(db.Integer, default=0, nullable=False)
    start_zone = db.Column(None, db.ForeignKey("zone.id"), nullable=False)
    end_zone = db.Column(None, db.ForeignKey("zone.id"), nullable=False)


class Bonus(db.Model):
    id_ = db.Column("id", db.Integer, primary_key=True)
    map_id = db.Column(None, db.ForeignKey("map.id"), nullable=False)
    bonus_index = db.Column(db.Integer, nullable=False)
    stier = db.Column(db.Integer, default=0, nullable=False)
    dtier = db.Column(db.Integer, default=0, nullable=False)
    s_completions = db.Column(db.Integer, default=0, nullable=False)
    d_completions = db.Column(db.Integer, default=0, nullable=False)
    start_zone = db.Column(None, db.ForeignKey("zone.id"), nullable=False)
    end_zone = db.Column(None, db.ForeignKey("zone.id"), nullable=False)


class MapCheckpoint(db.Model):
    id_ = db.Column("id", db.Integer, primary_key=True)
    zone_id = db.Column(None, db.ForeignKey("zone.id"), nullable=False)
    map_id = db.Column(None, db.ForeignKey("map.id"), nullable=False)
    cp_index = db.Column(db.Integer, nullable=False)


class CourseCheckpoint(db.Model):
    id_ = db.Column("id", db.Integer, primary_key=True)
    zone_id = db.Column(None, db.ForeignKey("zone.id"), nullable=False)
    course_id = db.Column(None, db.ForeignKey("course.id"), nullable=False)
    cp_index = db.Column(db.Integer, nullable=False)


class BonusCheckpoint(db.Model):
    id_ = db.Column("id", db.Integer, primary_key=True)
    zone_id = db.Column(None, db.ForeignKey("zone.id"), nullable=False)
    bonus_id = db.Column(None, db.ForeignKey("bonus.id"), nullable=False)
    cp_index = db.Column(db.Integer, nullable=False)


class MapTimes(db.Model):
    id_ = db.Column("id", db.Integer, primary_key=True)
    map_id = db.Column(None, db.ForeignKey("map.id"), nullable=False)
    player_id = db.Column(None, db.ForeignKey("player.id"), nullable=False)
    player_class = db.Column(db.Integer, nullable=False)
    start_time = db.Column(db.Double, nullable=False)
    end_time = db.Column(db.Double, nullable=False)
    rank = db.Column(db.Integer, nullable=False)

    @property
    def serialize(self):
        player = Player.query.filter_by(id_=self.player_id).first()
        if player is None:
            return {
                "id": self.id_,
                "map_id": self.map_id,
                "player_id": self.player_id,
                "class": self.player_class,
                "time": self.end_time - self.start_time,
                "rank": self.rank,
            }
        else:
            return {
                "id": self.id_,
                "map_id": self.map_id,
                "player": player.serialize(),
                "class": self.player_class,
                "time": self.end_time - self.start_time,
                "rank": self.rank,
            }


class CourseTimes(db.Model):
    id_ = db.Column("id", db.Integer, primary_key=True)
    course_id = db.Column(None, db.ForeignKey("course.id"), nullable=False)
    player_id = db.Column(None, db.ForeignKey("player.id"), nullable=False)
    player_class = db.Column(db.Integer, nullable=False)
    start_time = db.Column(db.Double, nullable=False)
    end_time = db.Column(db.Double, nullable=False)
    rank = db.Column(db.Integer, nullable=False)


class BonusTimes(db.Model):
    id_ = db.Column("id", db.Integer, primary_key=True)
    bonus_id = db.Column(None, db.ForeignKey("bonus.id"), nullable=False)
    player_id = db.Column(None, db.ForeignKey("player.id"), nullable=False)
    player_class = db.Column(db.Integer, nullable=False)
    start_time = db.Column(db.Double, nullable=False)
    end_time = db.Column(db.Double, nullable=False)
    rank = db.Column(db.Integer, nullable=False)


class MapCheckpointTimes(db.Model):
    id_ = db.Column("id", db.Integer, primary_key=True)
    checkpoint_id = db.Column(None, db.ForeignKey("map_checkpoint.id"), nullable=False)
    time_id = db.Column(None, db.ForeignKey("map_times.id"), nullable=False)
    time = db.Column(db.Double, nullable=False)


class CourseCheckpointTimes(db.Model):
    id_ = db.Column("id", db.Integer, primary_key=True)
    checkpoint_id = db.Column(
        None, db.ForeignKey("course_checkpoint.id"), nullable=False
    )
    time_id = db.Column(None, db.ForeignKey("course_times.id"), nullable=False)
    time = db.Column(db.Double, nullable=False)


class MapCheckpointTimes(db.Model):
    id_ = db.Column("id", db.Integer, primary_key=True)
    checkpoint_id = db.Column(
        None, db.ForeignKey("bonus_checkpoint.id"), nullable=False
    )
    time_id = db.Column(None, db.ForeignKey("bonus_times.id"), nullable=False)
    time = db.Column(db.Double, nullable=False)


class User(db.Model):
    """Model for authenticating restricted views"""

    id_ = db.Column("id", db.Integer, primary_key=True)
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

    id_ = db.Column("id", db.Integer, primary_key=True)
    jti = db.Column("jti", db.String(120), nullable=False)

    def add(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def is_jti_blacklisted(cls, jti):
        query = cls.query.filter_by(jti=jti).first()
        return bool(query)
