"""
Service BigQuery : logique de similarité utilisateurs et recommandations ML.
"""

import os
from google.cloud import bigquery
from google.oauth2 import service_account

PROJECT_ID = os.getenv("GCP_PROJECT_ID", "recommender-490715")
DATASET    = os.getenv("BQ_DATASET", "recommencer")
MODEL_REF  = f"{PROJECT_ID}.{DATASET}.mf_recommender"
RATINGS    = f"{PROJECT_ID}.{DATASET}.Ratings_train"
LINKS      = f"{PROJECT_ID}.{DATASET}.Links_train"
MOVIES     = f"{PROJECT_ID}.{DATASET}.Movies_train"
MOVIES_CATALOG = "project-8adb6d58-9682-4d77-8f2.Assignment_1.Movies"


def print_sql_debug(query: str, params: list = None, results: list = None):
    print("\n" + "="*60)
    print("Executing SQL query:")
    print(query.strip())
    if params:
        print("\nQuery parameters:")
        for p in params:
            val = getattr(p, "value", getattr(p, "values", None))
            print(f"- {p.name}: {val}")
    if results is not None:
        print(f"\nRows returned: {len(results)}")
        print("\nResult preview (first 3 rows):")
        for r in results[:3]:
            print(r)
    print("="*60 + "\n")
def _get_client() -> bigquery.Client:
    """Crée le client BigQuery depuis le fichier de credentials ou l'env."""
    key_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if key_path and os.path.exists(key_path):
        creds = service_account.Credentials.from_service_account_file(key_path)
        return bigquery.Client(project=PROJECT_ID, credentials=creds)
    return bigquery.Client(project=PROJECT_ID)


def find_similar_users(movie_ids: list[int], top_k: int = 5) -> list[int]:
    """
    Trouve les top-k utilisateurs les plus similaires à l'utilisateur courant.
    La similarité est basée sur le nombre de films en commun bien notés (rating_im >= 0.7).
    """
    if not movie_ids:
        return []

    client = _get_client()

    query = f"""
        SELECT userId, COUNT(*) AS common_movies
        FROM `{RATINGS}`
        WHERE movieId IN UNNEST(@movie_ids)
          AND rating_im >= 0.7
        GROUP BY userId
        ORDER BY common_movies DESC
        LIMIT @top_k
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ArrayQueryParameter("movie_ids", "INT64", movie_ids),
            bigquery.ScalarQueryParameter("top_k", "INT64", top_k),
        ]
    )
    print(f"[BQ] Recherche utilisateurs similaires pour movieIds: {movie_ids}")
    rows = list(client.query(query, job_config=job_config).result())
    similar_users = [row.userId for row in rows]
    
    # Log SQL and preview
    preview = [{"userId": row.userId, "common_movies": row.common_movies} for row in rows]
    print_sql_debug(query, job_config.query_parameters, preview)
    
    return similar_users


def get_recommendations_for_users(
    similar_user_ids: list[int],
    exclude_movie_ids: list[int],
    top_n: int = 10,
) -> list[dict]:
    """
    Génère des recommandations de films via ML.RECOMMEND pour les utilisateurs similaires.
    Exclut les films déjà sélectionnés par l'utilisateur.
    """
    if not similar_user_ids:
        return []

    client = _get_client()

    # Construit la liste des userIds pour la clause UNNEST
    user_ids_str = ", ".join(str(u) for u in similar_user_ids)
    exclude_str  = ", ".join(str(m) for m in exclude_movie_ids) if exclude_movie_ids else "NULL"

    query = f"""
        SELECT
          r.movieId,
          AVG(r.predicted_rating_im_confidence) AS score,
          m.title,
          m.genres,
          l.tmdbId
        FROM (
          SELECT movieId, predicted_rating_im_confidence,
                 ROW_NUMBER() OVER (
                   PARTITION BY userId
                   ORDER BY predicted_rating_im_confidence DESC
                 ) AS rn
          FROM ML.RECOMMEND(
            MODEL `{MODEL_REF}`,
            (SELECT userId FROM UNNEST([{user_ids_str}]) AS userId)
          )
        ) r
        JOIN `{MOVIES}` m ON r.movieId = m.movieId
        LEFT JOIN `{LINKS}` l ON r.movieId = l.movieId
        WHERE r.rn <= 20
          AND r.movieId NOT IN ({exclude_str})
        GROUP BY r.movieId, m.title, m.genres, l.tmdbId
        ORDER BY score DESC
        LIMIT {top_n}
    """

    print(f"[BQ] Recommandations pour users {similar_user_ids}, exclus: {exclude_movie_ids}")
    rows = list(client.query(query).result())
    results = []
    for row in rows:
        results.append({
            "movieId": row.movieId,
            "title":   row.title,
            "genres":  row.genres,
            "tmdbId":  row.tmdbId,
            "score":   round(float(row.score), 4),
        })
    print_sql_debug(query, None, results)
    return results


def get_total_movie_count() -> int:
    """Retourne le nombre total de films distincts dans le catalogue complet."""
    client = _get_client()
    query = f"SELECT COUNT(DISTINCT movieId) AS total FROM `{MOVIES_CATALOG}`"
    try:
        rows = list(client.query(query).result())
        return rows[0].total if rows else 0
    except Exception as e:
        print(f"[BQ] get_total_movie_count ERREUR: {e}")
        return 0


def get_popular_movies(top_n: int = 10) -> list[dict]:
    """
    Retourne les films les plus populaires basés sur la moyenne des ratings implicites.
    Utilisé quand aucun film n'est sélectionné (cold start sans préférence).
    """
    client = _get_client()

    query = f"""
        SELECT
          r.movieId,
          AVG(r.rating_im) AS avg_rating,
          COUNT(*) AS nb_ratings,
          m.title,
          m.genres,
          l.tmdbId
        FROM `{RATINGS}` r
        JOIN `{MOVIES}` m ON r.movieId = m.movieId
        LEFT JOIN `{LINKS}` l ON r.movieId = l.movieId
        GROUP BY r.movieId, m.title, m.genres, l.tmdbId
        HAVING nb_ratings >= 50
        ORDER BY avg_rating DESC, nb_ratings DESC
        LIMIT {top_n}
    """
    print("[BQ] Récupération des films populaires")
    rows = list(client.query(query).result())
    results = []
    for row in rows:
        results.append({
            "movieId":    row.movieId,
            "title":      row.title,
            "genres":     row.genres,
            "tmdbId":     row.tmdbId,
            "avg_rating": round(float(row.avg_rating), 4),
            "nb_ratings": row.nb_ratings,
        })
    print_sql_debug(query, None, results)
    return results
