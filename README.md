# ReelPick - Movie Recommendation Website

A full-stack movie recommendation site built with **Flask**, **SQLAlchemy** and plain **HTML/CSS/JS**.

## Features
- Home page: hero, trending, top rated, browse by genre, "Recommended for you"
- Search, filter (genre, year, min rating) and sort
- Movie details with cast, ratings and similar movies
- Register / login / logout (hashed passwords, sessions)
- 1-5 star ratings and a personal watchlist
- Content-based recommender (genre + description similarity, pure Python)
- 50 seeded movies, JSON API (`/api/movies`, `/api/recommendations`)

## Tech stack
Flask · Flask-SQLAlchemy · SQLite (local) / PostgreSQL (production) · Vercel

## Database tables
`user`, `movie`, `rating`, `watchlist` (foreign keys: rating/watchlist -> user, movie)

## Run locally
```
python -m venv venv
venv\Scripts\activate          # Windows   |  source venv/bin/activate (Mac/Linux)
pip install -r requirements.txt
python app.py
```
Open http://127.0.0.1:5000 . Tables are created and 50 movies are seeded automatically on first run.

## Deploy on Vercel
1. Create a free PostgreSQL database on Neon or Supabase and copy its connection string.
2. Push this repo to GitHub.
3. On vercel.com: Add New -> Project -> import the repo.
4. Add environment variables: `SECRET_KEY`, `DATABASE_URL`, `ADMIN_KEY`.
5. Deploy. The first visit creates tables and seeds movies.

## Screenshots
(Add screenshots of Home, Browse, Details and Watchlist here.)

## Add a movie via API
```
curl -X POST URL/api/movies -H "X-Admin-Key: YOUR_KEY" -H "Content-Type: application/json" \
  -d '{"title":"My Movie","genres":"Drama,Comedy","year":2024,"rating":7.5}'
```
