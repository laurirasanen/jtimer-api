from jtimer.extensions import db
from passlib.hash import bcrypt
from enum import Enum
from jtimer.points import calc_points


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

    @property
    def serialize(self):
        return {
            "id": self.id_,
            "p1": [self.x1, self.y1, self.z1],
            "p2": [self.x2, self.y2, self.z2],
        }

    def add(self):
        query = Zone.query.filter_by(id_=self.id_).first()
        if not query:
            db.session.add(self)
        db.session.commit()


class Map(db.Model):
    id_ = db.Column("id", db.Integer, primary_key=True)
    mapname = db.Column(db.String(128), nullable=False)
    stier = db.Column(db.Integer, default=0, nullable=False)
    dtier = db.Column(db.Integer, default=0, nullable=False)
    s_completions = db.Column(db.Integer, default=0, nullable=False)
    d_completions = db.Column(db.Integer, default=0, nullable=False)
    start_zone = db.Column(None, db.ForeignKey("zone.id"), nullable=True)
    end_zone = db.Column(None, db.ForeignKey("zone.id"), nullable=True)

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

    def add(self):
        query = Map.query.filter(
            Map.mapname == self.name or Map.id_ == self.id_
        ).first()
        if not query:
            db.session.add(self)

        db.session.commit()


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

    @property
    def serialize(self):
        zone = Zone.query.filter_by(id_=self.zone_id).first()
        zone_dict = None
        if zone:
            zone_dict = zone.serialize()

        return {
            "id": self.id_,
            "zone_type": "cp",
            "map_id": self.map_id,
            "cp_index": self.cp_index,
            "zone": zone_dict,
        }

    def add(self):
        query = MapCheckpoint.query.filter_by(id_=self.id_).first()
        if not query:
            db.session.add(self)
        db.session.commit()


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
    start_time = db.Column(db.Float(precision=53), nullable=False)
    end_time = db.Column(db.Float(precision=53), nullable=False)
    duration = db.Column(db.Float(precision=53), nullable=False)
    rank = db.Column(db.Integer, nullable=True)
    points = db.Column(db.Integer, nullable=True)

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

    def add(self):
        query = MapTimes.query.filter(
            MapTimes.map_id == self.map_id
            and MapTimes.player_id == self.player_id
            and MapTimes.player_class == self.player_class
        ).first()
        if not bool(query):
            # no existing run, add this
            db.session.add(self)
            db.session.commit()
            # update ranks
            completions = MapTimes.update_ranks(self.map_id)
            return {
                "result": InsertResult.ADDED,
                "rank": self.rank,
                "completions": completions,
                "points_gained": self.points,
            }
        else:
            # time already exists, check if faster
            old_time = query.end_time - query.start_time
            new_time = self.end_time - self.start_time
            old_points = query.points
            if new_time < old_time:
                improvement = old_time - new_time
                # faster, add this
                db.session.add(self)
                # remove old time
                db.session.delete(query)
                db.session.commit()
                # update ranks
                completions = MapTimes.update_ranks(self.map_id)
                return {
                    "result": InsertResult.UPDATED,
                    "rank": self.rank,
                    "points_gained": self.points - old_points,
                    "completions": completions,
                    "improvement": improvement,
                }
            else:
                # slower
                return {"result": InsertResult.NONE}

    @classmethod
    def update_ranks(map_id):
        times = (
            MapTimes.query.filter(MapTimes.map_id == map_id).order_by(duration).all()
        )
        if times:
            for i in range(0, len(times)):
                times[i].rank = i + 1
                times[i].points = calc_points(
                    times[0].duration, times[i].duration, len(times)
                )
            db.session.commit()
            return len(times)
        return 0


class CourseTimes(db.Model):
    id_ = db.Column("id", db.Integer, primary_key=True)
    course_id = db.Column(None, db.ForeignKey("course.id"), nullable=False)
    player_id = db.Column(None, db.ForeignKey("player.id"), nullable=False)
    player_class = db.Column(db.Integer, nullable=False)
    start_time = db.Column(db.Float(precision=53), nullable=False)
    end_time = db.Column(db.Float(precision=53), nullable=False)
    rank = db.Column(db.Integer, nullable=False)


class BonusTimes(db.Model):
    id_ = db.Column("id", db.Integer, primary_key=True)
    bonus_id = db.Column(None, db.ForeignKey("bonus.id"), nullable=False)
    player_id = db.Column(None, db.ForeignKey("player.id"), nullable=False)
    player_class = db.Column(db.Integer, nullable=False)
    start_time = db.Column(db.Float(precision=53), nullable=False)
    end_time = db.Column(db.Float(precision=53), nullable=False)
    rank = db.Column(db.Integer, nullable=False)


class MapCheckpointTimes(db.Model):
    id_ = db.Column("id", db.Integer, primary_key=True)
    checkpoint_id = db.Column(None, db.ForeignKey("map_checkpoint.id"), nullable=False)
    time_id = db.Column(None, db.ForeignKey("map_times.id"), nullable=False)
    time = db.Column(db.Float(precision=53), nullable=False)


class CourseCheckpointTimes(db.Model):
    id_ = db.Column("id", db.Integer, primary_key=True)
    checkpoint_id = db.Column(
        None, db.ForeignKey("course_checkpoint.id"), nullable=False
    )
    time_id = db.Column(None, db.ForeignKey("course_times.id"), nullable=False)
    time = db.Column(db.Float(precision=53), nullable=False)


class BonusCheckpointTimes(db.Model):
    id_ = db.Column("id", db.Integer, primary_key=True)
    checkpoint_id = db.Column(
        None, db.ForeignKey("bonus_checkpoint.id"), nullable=False
    )
    time_id = db.Column(None, db.ForeignKey("bonus_times.id"), nullable=False)
    time = db.Column(db.Float(precision=53), nullable=False)


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


class InsertResult(Enum):
    NONE = 0
    ADDED = 1
    UPDATED = 2
