import os
import json
import requests
import streamlit as st
from models.movie import Movie, MovieDetail

def print_debug(data):
    """Affiche les informations de debug SQL dans le terminal (stdout)."""
    debug = data.get('debug')
    if not debug:
        return
    
    print("\n" + "="*60)
    print("Executing SQL query:")
    print(debug.get('executed_sql', '').strip())
    
    print("\nQuery parameters:")
    print(json.dumps(debug.get('parameters', {}), default=str))
    
    print(f"\nRows returned: {debug.get('row_count', 0)}")
    
    print("\nResult preview:")
    print(json.dumps(debug.get('result_preview', []), default=str, indent=2))
    print("="*60 + "\n")

def fetch_filtered_movies(filters) -> list[Movie]:
    cloud_function_url = 'https://getmovies-1031393311197.europe-west6.run.app/get_movies'
    
    try:
        response = requests.post(cloud_function_url, json=filters)
        response.raise_for_status()
        data = response.json()
        
        # Afficher le debug SQL dans le terminal
        print_debug(data)
        
        raw_list = data.get('results', data if isinstance(data, list) else [])
        return [Movie.from_dict(m) for m in raw_list]
    except requests.RequestException as e:
        st.error(f"Erreur lors de la requête API: {e}")
        return []

def fetch_autocomplete(query, limit=5) -> list[str]:
    if not query or len(query) < 2:
        return []
        
    url = f"https://autocompletion-1031393311197.europe-west6.run.app/title_autocomplete?q={query}&limit={limit}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        # Afficher le debug SQL dans le terminal
        print_debug(data)
        
        return data.get('suggestions', [])
    except requests.RequestException:
        return []

@st.cache_data(ttl=3600)
def fetch_genres() -> list[str]:
    url = "https://getgenres-1031393311197.europe-west6.run.app/get_genres"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        # Afficher le debug SQL dans le terminal
        print_debug(data)
        
        return data.get('genres', [])
    except requests.RequestException:
        return []

def get_tmdb_preferred_poster(tmdb_id, api_key):
    try:
        url = f"https://api.themoviedb.org/3/movie/{tmdb_id}/images?api_key={api_key}&include_image_language=en,null"
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()

        posters = resp.json().get("posters", [])
        if posters:
            for p in posters:
                if p.get("iso_639_1") == "en":
                    return f"https://image.tmdb.org/t/p/w500{p['file_path']}"

            for p in posters:
                if p.get("iso_639_1") is None:
                    return f"https://image.tmdb.org/t/p/w500{p['file_path']}"

            return f"https://image.tmdb.org/t/p/w500{posters[0]['file_path']}"
    except:
        return None

    return None

def fetch_tmdb_movie_details(movie_id) -> MovieDetail | None:
    api_key = os.getenv('TMB_apikey', 'b26718e982f5c714c9bc4d5ba1f49dbd')
    
    if not api_key:
        st.error("La clé API pour TMDB est manquante. Vérifiez votre fichier .env.")
        return None

    url = f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}'
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        # Essaie de récupérer une affiche EN en priorité
        try:
            images_url = f'https://api.themoviedb.org/3/movie/{movie_id}/images?api_key={api_key}&include_image_language=en,null'
            images_response = requests.get(images_url, timeout=5)
            images_response.raise_for_status()
            posters = images_response.json().get("posters", [])

            preferred_poster_path = None

            for poster in posters:
                if poster.get("iso_639_1") == "en":
                    preferred_poster_path = poster.get("file_path")
                    break

            if not preferred_poster_path:
                for poster in posters:
                    if poster.get("iso_639_1") is None:
                        preferred_poster_path = poster.get("file_path")
                        break

            if not preferred_poster_path and posters:
                preferred_poster_path = posters[0].get("file_path")

            if preferred_poster_path:
                data["poster_path"] = preferred_poster_path

        except requests.RequestException:
            pass

        return MovieDetail.from_dict(data)

    except requests.RequestException as e:
        st.error(f"Erreur de communication avec l'API TMDB: {e}")
        return None
