"""
Service Elasticsearch : autocomplete des titres de films.
Utilise le même index movies_v2 que le Frontend Streamlit.
"""

import os
from elasticsearch import Elasticsearch
from dotenv import load_dotenv

load_dotenv()


def get_es_client() -> Elasticsearch:
    return Elasticsearch(
        os.getenv("ES_ENDPOINT"),
        api_key=os.getenv("ES_API_KEY"),
    )


def autocomplete_titles(query: str, limit: int = 8) -> list[dict]:
    """
    Retourne des suggestions de titres via Elasticsearch bool_prefix.
    Chaque suggestion contient le movieId (interne MovieLens) et le titre.
    """
    if not query or len(query) < 2:
        return []

    es = get_es_client()
    body = {
        "size": limit,
        "_source": ["title", "movieId"],
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
        print(f"[ES] autocomplete '{query}': {len(hits)} résultats")
        return [
            {
                "title":   hit["_source"].get("title", ""),
                "movieId": hit["_source"].get("movieId"),
            }
            for hit in hits
        ]
    except Exception as e:
        print(f"[ES] Erreur autocomplete: {e}")
        return []
