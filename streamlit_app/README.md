# 🎬 Movie Catalog — Cloud & Advanced Analytics
### Assignment 1 · HEC Lausanne

> Application Streamlit de catalogue de films déployée sur Google Cloud Run, connectée à BigQuery et à l'API TMDB.

**🔗 Live App :** [my-streamlit-app-1031393311197.europe-west6.run.app](https://my-streamlit-app-1031393311197.europe-west6.run.app/)

---

## Overview

This application allows users to explore a movie catalog built from `Movies.csv` and `Ratings.csv` datasets loaded into Google BigQuery. Users can browse, filter, and search movies, and view detailed information (poster, synopsis, budget, etc.) pulled in real-time from the **TMDB API**.

---

## Features

| Feature | Description |
|---|---|
| 🔍 **Smart Search** | Autocomplete search on movie titles via a dedicated Cloud Function |
| 🎛️ **Advanced Filters** | Filter by language, genre, minimum rating, and release year |
| 📖 **Movie Detail** | Fetches poster, synopsis, cast info, budget & revenue from TMDB |
| ☁️ **Cloud-native** | All data served through Google Cloud Functions backed by BigQuery |
| 📄 **Pagination** | Configurable page size (10 / 20 / 50 / 100 results) |

---

## Architecture

```
Streamlit App (Cloud Run)
       │
       ├── GET /get_genres       → Cloud Function → BigQuery
       ├── POST /get_movies      → Cloud Function → BigQuery
       ├── GET /title_autocomplete → Cloud Function → BigQuery
       └── GET /movie/{id}       → TMDB REST API
```

### Project Structure

```
streamlit_app/
├── main.py                  # Entry point & router
├── models/
│   └── movie.py             # Movie & MovieDetail dataclasses
├── api/
│   └── services.py          # All API/HTTP calls
├── views/
│   ├── landing.py           # Home page
│   ├── catalog.py           # Movie list + filters
│   └── movie_detail.py      # Movie detail page
├── ui/
│   └── styles.py            # Global CSS theme
└── .streamlit/
    └── config.toml          # Streamlit theme config
```

---

## Google Cloud Functions

> 📁 The source code for all Cloud Functions is available in the `cloud_functions/` directory at the root of this repository, organized by function name (`get_movies/`, `get_genres/`, `autocomplete/`).

### `getmovies` — POST `/get_movies`

Returns a paginated, filtered list of movies from BigQuery.

**Example payload:**
```json
{
    "page": 1,
    "page_size": 20,
    "title_prefix": "The",
    "language": "en",
    "genre": "Action",
    "min_avg_rating": 3.5,
    "released_after": 2000
}
```

**Query logic:** Joins `Movies` and `Ratings` tables, applies dynamic WHERE clauses, groups by movie, and filters on average rating via a HAVING clause.

```python
import functions_framework
from google.cloud import bigquery
import json

client = bigquery.Client()

@functions_framework.http
def get_movies(request):
    body = request.get_json(silent=True) or {}
    # ... dynamic SQL with parameterized filters
    # See full implementation in the Cloud Console
```

---

### `getgenres` — GET `/get_genres`

Returns a deduplicated, sorted list of all genres found in the dataset by unnesting the pipe-separated `genres` column.

```sql
SELECT DISTINCT TRIM(g) AS genre
FROM `project.Assignment_1.Movies`,
UNNEST(SPLIT(genres, '|')) AS g
WHERE TRIM(g) != '' AND TRIM(g) != '(no genres listed)'
ORDER BY genre
```

---

### `autocompletion` — GET `/title_autocomplete?q=<prefix>&limit=<n>`

Returns movie title suggestions matching the given prefix — used to power the search bar in real time.

```sql
SELECT DISTINCT title
FROM `project.Assignment_1.Movies`
WHERE LOWER(title) LIKE LOWER(CONCAT(@prefix, '%'))
ORDER BY title
LIMIT @limit
```

---

## SQL Query Logging (Assignment Requirement)

To satisfy the assignment requirement — *"display the executed SQL queries and their outputs in the terminal"* — each Cloud Function includes a `debug` object in its JSON response:

```json
{
  "results": [...],
  "debug": {
    "executed_sql": "SELECT ... FROM ... WHERE ...",
    "parameters": {"language": "en", "limit": 20},
    "row_count": 20,
    "result_preview": [{"title": "Inception", "avg_rating": 4.3}]
  }
}
```

The Streamlit app (`api/services.py`) reads this `debug` object and **prints it in the terminal (stdout)** for every API call. This produces output like:

```
============================================================
Executing SQL query:
SELECT m.movieId, m.title, ...
FROM `project.Assignment_1.Movies` m
LEFT JOIN `project.Assignment_1.Ratings` r ON r.movieId = m.movieId
WHERE m.language = @language
GROUP BY ...
ORDER BY avg_rating DESC
LIMIT @limit OFFSET @offset

Query parameters:
{"language": "en", "limit": 20, "offset": 0}

Rows returned: 20

Result preview:
[
  {"title": "Inception", "avg_rating": 4.3},
  {"title": "The Dark Knight", "avg_rating": 4.7}
]
============================================================
```

This logging is visible when running locally (`streamlit run main.py`), inside Docker, or on Cloud Run.

---

## Local Setup

```bash
# 1. Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment variables
cp .env.example .env   # then fill in TMB_apikey

# 4. Run the app
streamlit run main.py
```

---

## Environment Variables

| Variable | Description |
|---|---|
| `TMB_apikey` | Your TMDB API key (v3 auth) |

---

## Author

**Zakaria Charouite** — HEC Lausanne, Cloud & Advanced Analytics