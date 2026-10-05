"""Content-based recommendations in pure Python (no scikit-learn, so Vercel stays light).
Similarity = 70% genre overlap + 30% description keyword overlap (Jaccard)."""
import re
from models import Movie, Rating, Watchlist

STOP = {"with", "that", "from", "their", "this", "into", "have", "about", "after", "while"}


def _words(m):
    return {w for w in re.findall(r"[a-z]+", (m.description or "").lower()) if len(w) > 3 and w not in STOP}


def _jaccard(a, b):
    return len(a & b) / len(a | b) if a and b else 0.0


def similarity(a, b):
    return 0.7 * _jaccard(set(a.genre_list), set(b.genre_list)) + 0.3 * _jaccard(_words(a), _words(b))


def similar_movies(movie, n=6):
    others = Movie.query.filter(Movie.id != movie.id).all()
    others.sort(key=lambda m: (-similarity(movie, m), -(m.rating or 0)))
    return others[:n]


def recommend_for_user(user_id, n=8):
    """Recommend unseen movies most similar to the ones the user rated 4 or 5."""
    rated = {r.movie_id: r.score for r in Rating.query.filter_by(user_id=user_id)}
    saved = {w.movie_id for w in Watchlist.query.filter_by(user_id=user_id)}
    movies = Movie.query.all()
    liked = [m for m in movies if rated.get(m.id, 0) >= 4]
    if not liked:
        return []
    scored = [(sum(similarity(m, l) for l in liked) / len(liked), m)
              for m in movies if m.id not in rated and m.id not in saved]
    scored.sort(key=lambda x: (-x[0], -(x[1].rating or 0)))
    return [m for _, m in scored[:n]]
