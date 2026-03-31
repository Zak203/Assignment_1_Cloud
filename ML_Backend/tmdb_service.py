"""
Service TMDB : récupération des posters et métadonnées des films.
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

TMDB_API_KEY   = os.getenv("TMB_apikey")
TMDB_BASE_URL  = "https://api.themoviedb.org/3"
TMDB_IMG_BASE  = "https://image.tmdb.org/t/p/w500"


def enrich_with_posters(movies: list[dict]) -> list[dict]:
    """
    Enrichit une liste de films avec les posters et métadonnées TMDB.
    Chaque film doit avoir un champ 'tmdbId'.
    """
    enriched = []
    for movie in movies:
        tmdb_id = movie.get("tmdbId")
        if tmdb_id:
            details = fetch_tmdb_details(int(tmdb_id))
            if details:
                movie["poster_url"]   = details.get("poster_url")
                movie["overview"]     = details.get("overview", "")
                movie["release_year"] = details.get("release_year")
        enriched.append(movie)
    return enriched


def fetch_tmdb_details(tmdb_id: int) -> dict | None:
    """Appelle l'API TMDB pour récupérer les détails d'un film."""
    if not TMDB_API_KEY or not tmdb_id:
        return None

    url = f"{TMDB_BASE_URL}/movie/{tmdb_id}?api_key={TMDB_API_KEY}"
    try:
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        poster_path = data.get("poster_path")
        return {
            "poster_url":   f"{TMDB_IMG_BASE}{poster_path}" if poster_path else None,
            "overview":     data.get("overview", ""),
            "release_year": data.get("release_date", "")[:4] if data.get("release_date") else None,
        }
    except Exception as e:
        print(f"[TMDB] Erreur pour tmdb_id={tmdb_id}: {e}")
        return None
