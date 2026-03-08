import functions_framework
from google.cloud import bigquery
import json

client = bigquery.Client()

@functions_framework.http
def get_movies(request):
    body = request.get_json(silent=True) or {}

    title_prefix = body.get("title_prefix")
    language = body.get("language")
    genre = body.get("genre")
    min_avg_rating = body.get("min_avg_rating")
    released_after = body.get("released_after")

    page = int(body.get("page", 1))
    page_size = int(body.get("page_size", 20))
    offset = (page - 1) * page_size

    where = []
    params = []
    params_dict = {}

    if title_prefix:
        where.append("LOWER(m.title) LIKE LOWER(CONCAT(@title_prefix, '%'))")
        params.append(bigquery.ScalarQueryParameter("title_prefix", "STRING", title_prefix))
        params_dict["title_prefix"] = title_prefix

    if language:
        where.append("m.language = @language")
        params.append(bigquery.ScalarQueryParameter("language", "STRING", language))
        params_dict["language"] = language

    if released_after:
        where.append("m.release_year > @released_after")
        params.append(bigquery.ScalarQueryParameter("released_after", "INT64", int(released_after)))
        params_dict["released_after"] = int(released_after)

    if genre:
        where.append("LOWER(m.genres) LIKE LOWER(CONCAT('%', @genre, '%'))")
        params.append(bigquery.ScalarQueryParameter("genre", "STRING", genre))
        params_dict["genre"] = genre

    where_sql = "WHERE " + " AND ".join(where) if where else ""

    having = ""
    if min_avg_rating:
        having = "HAVING AVG(r.rating) >= @min_avg_rating"
        params.append(bigquery.ScalarQueryParameter("min_avg_rating", "FLOAT64", float(min_avg_rating)))
        params_dict["min_avg_rating"] = float(min_avg_rating)

    sql = f"""
    SELECT
        m.movieId,
        m.title,
        m.language,
        m.release_year,
        m.genres,
        m.tmdbId,
        AVG(r.rating) AS avg_rating
    FROM `project-8adb6d58-9682-4d77-8f2.Assignment_1.Movies` m
    LEFT JOIN `project-8adb6d58-9682-4d77-8f2.Assignment_1.Ratings` r
        ON r.movieId = m.movieId
    {where_sql}
    GROUP BY
        m.movieId,
        m.title,
        m.language,
        m.release_year,
        m.genres,
        m.tmdbId
    {having}
    ORDER BY avg_rating DESC
    LIMIT @limit
    OFFSET @offset
    """

    params.append(bigquery.ScalarQueryParameter("limit", "INT64", page_size))
    params.append(bigquery.ScalarQueryParameter("offset", "INT64", offset))
    params_dict["limit"] = page_size
    params_dict["offset"] = offset

    # Log SQL query to Cloud Function logs
    print(f"\nExecuting SQL query:\n{sql}")
    print(f"\nQuery parameters:\n{json.dumps(params_dict, default=str)}")

    job_config = bigquery.QueryJobConfig(query_parameters=params)

    try:
        rows = [dict(row) for row in client.query(sql, job_config=job_config).result()]

        print(f"\nRows returned: {len(rows)}")
        print(f"\nResult preview:\n{json.dumps(rows[:5], default=str)}")

        response_body = {
            "results": rows,
            "debug": {
                "executed_sql": sql,
                "parameters": params_dict,
                "row_count": len(rows),
                "result_preview": rows[:5]
            }
        }
        return (json.dumps(response_body, default=str), 200, {"Content-Type": "application/json"})
    except Exception as e:
        return (json.dumps({"error": str(e)}), 500, {"Content-Type": "application/json"})
