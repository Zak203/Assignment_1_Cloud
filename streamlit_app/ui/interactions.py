import streamlit as st
import requests
import os

TMDB_API_KEY = os.getenv("TMB_apikey", "b26718e982f5c714c9bc4d5ba1f49dbd")

def get_poster_url(tmdb_id):
    if not tmdb_id: return None
    try:
        url = f"https://api.themoviedb.org/3/movie/{tmdb_id}?api_key={TMDB_API_KEY}&language=fr-FR"
        resp = requests.get(url, timeout=3)
        if resp.status_code == 200:
            path = resp.json().get("poster_path")
            if path:
                return f"https://image.tmdb.org/t/p/w500{path}"
    except:
        pass
    return None

def toggle_like(movie_dict):
    """
    movie_dict must contain at least 'movieId', 'title', and preferably 'tmdbId' and 'poster_url'.
    """
    m_id = movie_dict.get('movieId')
    if not m_id: return
    
    if "liked_movies_data" not in st.session_state:
        st.session_state.liked_movies_data = {}
        
    if "liked_movies" not in st.session_state:
        st.session_state.liked_movies = set()

    if m_id in st.session_state.liked_movies:
        st.session_state.liked_movies.remove(m_id)
        if m_id in st.session_state.liked_movies_data:
            del st.session_state.liked_movies_data[m_id]
        st.session_state.is_loading_like = True
        st.toast("🗑️ Film retiré de votre liste")
    else:
        if not movie_dict.get("poster_url") and movie_dict.get("tmdbId"):
            movie_dict["poster_url"] = get_poster_url(movie_dict["tmdbId"])
            
        st.session_state.liked_movies.add(m_id)
        st.session_state.liked_movies_data[m_id] = movie_dict
        st.session_state.is_loading_like = True
        st.toast("❤️ Film ajouté à votre liste !")
