"""
Flask backend — Movie Recommender System
Routes principales :
  GET  /autocomplete?q=<query>  → suggestions de titres Elasticsearch
  POST /recommend               → recommandations personnalisées (cold-start)
  GET  /movies/popular          → films populaires (sans sélection)
"""

import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv

from bq_service   import find_similar_users, get_recommendations_for_users, get_popular_movies, get_total_movie_count
from es_service   import autocomplete_titles, fetch_all_movies_dict
from tmdb_service import enrich_with_posters

load_dotenv()

app = Flask(__name__)


@app.route("/health")
def health():
    return jsonify({"status": "ok"}), 200

@app.route("/movies/dict")
def movies_dict():
    """
    GET /movies/dict
    Retourne le dictionnaire de tous les films depuis ES pour initialiser les filtres du Frontend.
    """
    results = fetch_all_movies_dict()
    return jsonify(results)


@app.route("/autocomplete")
def autocomplete():
    """
    GET /autocomplete?q=star&limit=8
    Retourne une liste de suggestions de titres depuis Elasticsearch.
    """
    query = request.args.get("q", "").strip()
    limit = int(request.args.get("limit", 8))
    suggestions = autocomplete_titles(query, limit=limit)
    return jsonify({"suggestions": suggestions})


@app.route("/recommend", methods=["POST"])
def recommend():
    data      = request.get_json(force=True) or {}
    movie_ids = [int(m) for m in data.get("movie_ids", [])]
    top_n     = int(data.get("top_n", 10))
    fetch_posters = data.get("posters", True)

    print(f"[RECOMMEND] Requête reçue — movie_ids={movie_ids}, top_n={top_n}, posters={fetch_posters}")

    if not movie_ids:
        movies = get_popular_movies(top_n=top_n)
        if fetch_posters: movies = enrich_with_posters(movies)
        return jsonify({"type": "popular", "results": movies})

    similar_users = find_similar_users(movie_ids, top_k=5)

    if not similar_users:
        movies = get_popular_movies(top_n=top_n)
        if fetch_posters: movies = enrich_with_posters(movies)
        return jsonify({"type": "popular_fallback", "results": movies})

    recommendations = get_recommendations_for_users(
        similar_user_ids=similar_users,
        exclude_movie_ids=movie_ids,
        top_n=top_n,
    )

    if fetch_posters:
        recommendations = enrich_with_posters(recommendations)

    return jsonify({
        "type":          "personalized",
        "similar_users": similar_users,
        "results":       recommendations,
    })


@app.route("/movies/count")
def movies_count():
    """GET /movies/count — Nombre total de films dans BigQuery."""
    total = get_total_movie_count()
    return jsonify({"total": total})


@app.route("/movies/popular")
def popular():
    top_n  = int(request.args.get("top_n", 10))
    fetch_posters = request.args.get("posters", "true").lower() == "true"
    
    movies = get_popular_movies(top_n=top_n)
    if fetch_posters:
        movies = enrich_with_posters(movies)
        
    return jsonify({"type": "popular", "results": movies})


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
