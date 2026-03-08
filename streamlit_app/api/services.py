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

def fetch_tmdb_movie_details(movie_id) -> MovieDetail | None:
    api_key = os.getenv('TMB_apikey')
    
    if not api_key:
        st.error("La clé API pour TMDB est manquante. Vérifiez votre fichier .env.")
        return None

    url = f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}'
    try:
        response = requests.get(url)
        response.raise_for_status()
        return MovieDetail.from_dict(response.json())
    except requests.RequestException as e:
        st.error(f"Erreur de communication avec l'API TMDB: {e}")
        return None
