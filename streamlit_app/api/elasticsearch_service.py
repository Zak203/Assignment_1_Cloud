import os
import requests
import streamlit as st

ML_BACKEND_URL = os.getenv("ML_BACKEND_URL", "http://127.0.0.1:5001")

@st.cache_data(ttl=86400)
def fetch_total_movie_count() -> int:
    """Récupère le nombre total de films depuis BigQuery via le backend ML."""
    try:
        response = requests.get(f"{ML_BACKEND_URL}/movies/count", timeout=10)
        response.raise_for_status()
        return response.json().get("total", 0)
    except Exception as e:
        print(f"[API] fetch_total_movie_count ERREUR: {e}")
        return 0


@st.cache_data(ttl=3600)
def fetch_all_movies_dict() -> dict[str, dict]:
    """Récupère tous les films depuis le backend ML (qui lui contacte Elasticsearch)."""
    try:
        response = requests.get(f"{ML_BACKEND_URL}/movies/dict", timeout=15)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"[API] fetch_all_movies_dict ERREUR: {e}")
        return {}

def autocomplete_titles(query: str, limit: int = 5) -> list[str]:
    """Retourne des suggestions depuis le backend ML."""
    if not query or len(query) < 2:
        return []

    try:
        response = requests.get(
            f"{ML_BACKEND_URL}/autocomplete", 
            params={"q": query, "limit": limit},
            timeout=5
        )
        response.raise_for_status()
        data = response.json()
        suggestions = data.get("suggestions", [])
        return [s.get("title") for s in suggestions if isinstance(s, dict) and "title" in s]
    except Exception as e:
        print(f"[API] autocomplete_titles ERREUR: {e}")
        return []
