import os
from elasticsearch import Elasticsearch
from dotenv import load_dotenv
import streamlit as st

load_dotenv()

@st.cache_resource
def get_es_client() -> Elasticsearch:
    return Elasticsearch(
        os.getenv("ES_ENDPOINT"),
        api_key=os.getenv("ES_API_KEY"),
    )


@st.cache_data(ttl=3600)
def fetch_all_titles() -> list[str]:
    """Récupère tous les titres uniques depuis Elasticsearch (mis en cache 1h)."""
    es = get_es_client()
    try:
        response = es.search(
            index="movies_v2",
            body={
                "size": 10000,
                "_source": ["title"],
                "query": {"match_all": {}},
            },
        )
        hits = response["hits"]["hits"]
        print(f"[ES] fetch_all_titles: {len(hits)} hits trouvés")
        titles = sorted(set(hit["_source"]["title"] for hit in hits if "title" in hit["_source"]))
        return titles
    except Exception as e:
        print(f"[ES] fetch_all_titles ERREUR: {e}")
        return []

@st.cache_data(ttl=3600)
def fetch_all_movies_dict() -> dict[str, dict]:
    """Récupère tous les films (titre -> dict avec movieId, tmdbId, language) depuis Elasticsearch."""
    es = get_es_client()
    try:
        response = es.search(
            index="movies_v2",
            body={
                "size": 10000,
                "_source": ["title", "movieId", "tmdbId", "language"],
                "query": {"match_all": {}},
            },
        )
        hits = response["hits"]["hits"]
        movies_dict = {}
        for hit in hits:
            src = hit["_source"]
            if "title" in src:
                movies_dict[src["title"]] = {
                    "movieId": src.get("movieId"),
                    "tmdbId": src.get("tmdbId"),
                    "language": src.get("language")
                }
        return movies_dict
    except Exception as e:
        print(f"[ES] fetch_all_movies_dict ERREUR: {e}")
        return {}



def autocomplete_titles(query: str, limit: int = 5) -> list[str]:
    """Retourne jusqu'à `limit` suggestions de titres via Elasticsearch bool_prefix."""
    if not query or len(query) < 2:
        return []

    es = get_es_client()

    body = {
        "size": limit,
        "_source": ["title"],
        "query": {
            "multi_match": {
                "query": query,
                "type": "bool_prefix",
                "fields": ["title", "title._2gram", "title._3gram"],
            }
        },
    }

    try:
        response = es.search(index="movies_v2", body=body)
        hits = response["hits"]["hits"]
        return [hit["_source"]["title"] for hit in hits]
    except Exception:
        return []
