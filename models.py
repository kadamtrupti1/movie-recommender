from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    ratings = db.relationship("Rating", backref="user", cascade="all, delete")
    watchlist = db.relationship("Watchlist", backref="user", cascade="all, delete")

    def set_password(self, pw):
        self.password_hash = generate_password_hash(pw)

    def check_password(self, pw):
        return check_password_hash(self.password_hash, pw)


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    year = db.Column(db.Integer)
    rating = db.Column(db.Float, default=0)          # critic/IMDb-style score
    genres = db.Column(db.String(200), nullable=False)  # "Action,Sci-Fi"
    cast = db.Column(db.String(300))
    description = db.Column(db.Text)
    poster_url = db.Column(db.String(500))
    popularity = db.Column(db.Integer, default=0)    # used for "Trending"
    ratings = db.relationship("Rating", backref="movie", cascade="all, delete")

    @property
    def genre_list(self):
        return [g.strip() for g in self.genres.split(",") if g.strip()]

    def to_dict(self):
        return dict(id=self.id, title=self.title, year=self.year, rating=self.rating,
                    genres=self.genre_list, cast=self.cast, description=self.description,
                    poster_url=self.poster_url)


class Rating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    movie_id = db.Column(db.Integer, db.ForeignKey("movie.id"), nullable=False)
    score = db.Column(db.Integer, nullable=False)    # 1-5
    __table_args__ = (db.UniqueConstraint("user_id", "movie_id"),)


class Watchlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    movie_id = db.Column(db.Integer, db.ForeignKey("movie.id"), nullable=False)
    movie = db.relationship("Movie")
    __table_args__ = (db.UniqueConstraint("user_id", "movie_id"),)
