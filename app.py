import os
from functools import wraps
from flask import (Flask, render_template, request, redirect, url_for,
                   session, flash, jsonify, g)
from sqlalchemy import func
from models import db, User, Movie, Rating, Watchlist
from recommender import similar_movies, recommend_for_user

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-change-me")

# --- Database config: PostgreSQL if DATABASE_URL is set, otherwise SQLite ---
uri = os.getenv("DATABASE_URL")
if uri:
    uri = uri.replace("postgres://", "postgresql://", 1)
else:
    base = os.path.dirname(os.path.abspath(__file__))
    path = "/tmp/movies.db" if os.getenv("VERCEL") else os.path.join(base, "movies.db")
    uri = "sqlite:///" + path
app.config["SQLALCHEMY_DATABASE_URI"] = uri
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

# Create tables and load sample movies automatically on first start
with app.app_context():
    db.create_all()
    if Movie.query.count() == 0:
        from seed import seed
        seed()


# ---------------- helpers ----------------
@app.before_request
def load_user():
    uid = session.get("user_id")
    g.user = db.session.get(User, uid) if uid else None


@app.context_processor
def inject_user():
    return {"current_user": g.user}


def login_required(f):
    @wraps(f)
    def wrapper(*a, **kw):
        if g.user is None:
            if request.is_json:
                return jsonify(error="login required"), 401
            flash("Please log in first.")
            return redirect(url_for("login"))
        return f(*a, **kw)
    return wrapper


def to_num(value, cast):
    try:
        return cast(value)
    except (TypeError, ValueError):
        return None


def all_genres():
    names = set()
    for (gs,) in db.session.query(Movie.genres).all():
        names.update(x.strip() for x in gs.split(","))
    return sorted(names)


# ---------------- pages ----------------
@app.route("/")
def index():
    trending = Movie.query.order_by(Movie.popularity.desc()).limit(8).all()
    top = Movie.query.order_by(Movie.rating.desc()).limit(8).all()
    recs = recommend_for_user(g.user.id) if g.user else []
    return render_template("index.html", hero=trending[0] if trending else None,
                           trending=trending, top=top, recs=recs, genres=all_genres())


@app.route("/movies")
def movies():
    q = request.args.get("q", "").strip()
    genre = request.args.get("genre", "")
    year = to_num(request.args.get("year"), int)
    min_rating = to_num(request.args.get("min_rating"), float)
    sort = request.args.get("sort", "popular")

    query = Movie.query
    if q:
        query = query.filter(Movie.title.ilike(f"%{q}%"))
    if genre:
        query = query.filter(Movie.genres.ilike(f"%{genre}%"))
    if year:
        query = query.filter(Movie.year >= year)
    if min_rating:
        query = query.filter(Movie.rating >= min_rating)
    order = {"rating": Movie.rating.desc(), "year": Movie.year.desc(),
             "title": Movie.title.asc(), "popular": Movie.popularity.desc()}
    results = query.order_by(order.get(sort, Movie.popularity.desc())).all()
    return render_template("movies.html", movies=results, genres=all_genres(),
                           q=q, genre=genre, year=year or "", min_rating=min_rating or "", sort=sort)


@app.route("/movie/<int:movie_id>")
def detail(movie_id):
    movie = db.get_or_404(Movie, movie_id)
    my, in_list = None, False
    if g.user:
        my = Rating.query.filter_by(user_id=g.user.id, movie_id=movie_id).first()
        in_list = Watchlist.query.filter_by(user_id=g.user.id, movie_id=movie_id).first() is not None
    avg, count = db.session.query(func.avg(Rating.score), func.count(Rating.id)) \
        .filter(Rating.movie_id == movie_id).first()
    return render_template("detail.html", movie=movie, my=my, in_list=in_list,
                           avg=round(avg, 1) if avg else 0, count=count,
                           similar=similar_movies(movie))


@app.route("/watchlist")
@login_required
def watchlist():
    items = Watchlist.query.filter_by(user_id=g.user.id).all()
    return render_template("watchlist.html", movies=[w.movie for w in items])


# ---------------- auth ----------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        if not username or not email or len(password) < 6:
            flash("Fill all fields. Password needs at least 6 characters.")
        elif User.query.filter((User.email == email) | (User.username == username)).first():
            flash("Username or email already registered.")
        else:
            user = User(username=username, email=email)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            session["user_id"] = user.id
            flash("Welcome! Rate a few movies to get recommendations.")
            return redirect(url_for("index"))
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = User.query.filter_by(email=request.form.get("email", "").strip().lower()).first()
        if user and user.check_password(request.form.get("password", "")):
            session["user_id"] = user.id
            return redirect(url_for("index"))
        flash("Wrong email or password.")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


# ---------------- actions (called from JavaScript) ----------------
@app.post("/rate/<int:movie_id>")
@login_required
def rate(movie_id):
    db.get_or_404(Movie, movie_id)
    score = to_num((request.get_json(silent=True) or {}).get("score"), int)
    if score not in (1, 2, 3, 4, 5):
        return jsonify(error="score must be 1-5"), 400
    r = Rating.query.filter_by(user_id=g.user.id, movie_id=movie_id).first()
    if r:
        r.score = score
    else:
        db.session.add(Rating(user_id=g.user.id, movie_id=movie_id, score=score))
    db.session.commit()
    avg, count = db.session.query(func.avg(Rating.score), func.count(Rating.id)) \
        .filter(Rating.movie_id == movie_id).first()
    return jsonify(ok=True, avg=round(avg, 1), count=count)


@app.post("/watchlist/<int:movie_id>")
@login_required
def toggle_watchlist(movie_id):
    db.get_or_404(Movie, movie_id)
    w = Watchlist.query.filter_by(user_id=g.user.id, movie_id=movie_id).first()
    if w:
        db.session.delete(w)
    else:
        db.session.add(Watchlist(user_id=g.user.id, movie_id=movie_id))
    db.session.commit()
    return jsonify(in_list=w is None)


# ---------------- JSON API ----------------
@app.get("/api/movies")
def api_movies():
    q = request.args.get("q", "")
    items = Movie.query.filter(Movie.title.ilike(f"%{q}%")).limit(50).all()
    return jsonify([m.to_dict() for m in items])


@app.get("/api/recommendations")
@login_required
def api_recs():
    return jsonify([m.to_dict() for m in recommend_for_user(g.user.id)])


@app.post("/api/movies")
def api_add_movie():
    """Admin: send header X-Admin-Key and JSON {title, genres, year, rating, description, cast, poster_url}"""
    if request.headers.get("X-Admin-Key") != os.getenv("ADMIN_KEY", "my-admin-key"):
        return jsonify(error="forbidden"), 403
    d = request.get_json(silent=True) or {}
    if not d.get("title") or not d.get("genres"):
        return jsonify(error="title and genres required"), 400
    m = Movie(title=d["title"], genres=d["genres"], year=d.get("year"), rating=d.get("rating", 0),
              description=d.get("description", ""), cast=d.get("cast", ""),
              poster_url=d.get("poster_url", ""), popularity=50)
    db.session.add(m)
    db.session.commit()
    return jsonify(m.to_dict()), 201


if __name__ == "__main__":
    app.run(debug=True)
