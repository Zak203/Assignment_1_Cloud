import functions_framework
from google.cloud import bigquery
import json

client = bigquery.Client()

@functions_framework.http
def title_autocomplete(request):
    prefix = request.args.get("q", "")
    limit = int(request.args.get("limit", 10))

    sql = """
    SELECT DISTINCT title
    FROM `project-8adb6d58-9682-4d77-8f2.Assignment_1.Movies`
    WHERE LOWER(title) LIKE LOWER(CONCAT(@prefix, '%'))
    ORDER BY title
    LIMIT @limit
    """

    params_dict = {"prefix": prefix, "limit": limit}

    # Log SQL query to Cloud Function logs
    print(f"\nExecuting SQL query:\n{sql}")
    print(f"\nQuery parameters:\n{json.dumps(params_dict)}")

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("prefix", "STRING", prefix),
            bigquery.ScalarQueryParameter("limit", "INT64", limit),
        ]
    )

    try:
        rows = [row["title"] for row in client.query(sql, job_config=job_config).result()]

        print(f"\nRows returned: {len(rows)}")
        print(f"\nResult preview:\n{json.dumps(rows[:5], default=str)}")

        response_body = {
            "suggestions": rows,
            "debug": {
                "executed_sql": sql,
                "parameters": params_dict,
                "row_count": len(rows),
                "result_preview": rows[:5]
            }
        }
        return (
            json.dumps(response_body, default=str),
            200,
            {"Content-Type": "application/json"},
        )
    except Exception as e:
        return (
            json.dumps({"error": str(e)}),
            500,
            {"Content-Type": "application/json"},
        )
