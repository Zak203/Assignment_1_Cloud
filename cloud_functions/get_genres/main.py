import functions_framework
from google.cloud import bigquery
import json

client = bigquery.Client()

@functions_framework.http
def get_genres(request):
    sql = """
        SELECT DISTINCT TRIM(g) AS genre
        FROM `project-8adb6d58-9682-4d77-8f2.Assignment_1.Movies`,
        UNNEST(SPLIT(genres, '|')) AS g
        WHERE g IS NOT NULL
          AND TRIM(g) != ''
          AND TRIM(g) != '(no genres listed)'
        ORDER BY genre
    """

    # Log SQL query to Cloud Function logs
    print(f"\nExecuting SQL query:\n{sql}")
    print(f"\nQuery parameters:\n{{}}")

    try:
        rows = client.query(sql).result()
        genres = [r["genre"] for r in rows]

        print(f"\nRows returned: {len(genres)}")
        print(f"\nResult preview:\n{json.dumps(genres[:5], default=str)}")

        response_body = {
            "genres": genres,
            "debug": {
                "executed_sql": sql,
                "parameters": {},
                "row_count": len(genres),
                "result_preview": genres[:5]
            }
        }
        return (
            json.dumps(response_body, default=str),
            200,
            {"Content-Type": "application/json"}
        )
    except Exception as e:
        return (
            json.dumps({"error": str(e)}),
            500,
            {"Content-Type": "application/json"}
        )
