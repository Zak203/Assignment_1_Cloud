import streamlit as st
import requests
import os
from dotenv import load_dotenv

if os.path.exists('.env'):
    load_dotenv('.env')
else:
    load_dotenv(dotenv_path='../.env')

st.set_page_config(page_title="Assignment 1 Movies", page_icon="🎬", layout="wide")

def apply_custom_styles():
    st.markdown(
        """
        <style>
        /* Global Background - Deep Space Navy */
        .stApp { background-color: #020617; }
        
        /* Main Container */
        .main .block-container { padding-top: 3rem; padding-bottom: 3rem; max-width: 1200px; }
        
        /* Glassmorphic Sidebar */
        [data-testid="stSidebar"] { 
            background-color: rgba(15, 23, 42, 0.95) !important; 
            border-right: 1px solid rgba(255, 255, 255, 0.1); 
        }
        
        /* Search Bar Glow */
        .st-keyup input {
            border-radius: 12px !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            padding: 0.7rem 1.2rem !important;
            background-color: rgba(30, 41, 59, 0.5) !important;
            color: #FFFFFF !important;
            transition: all 0.3s ease !important;
        }
        .st-keyup input:focus {
            border-color: #6366F1 !important;
            box-shadow: 0 0 15px rgba(99, 102, 241, 0.3) !important;
            background-color: rgba(30, 41, 59, 0.8) !important;
        }
        
        /* Glassmorphic Cards */
        .movie-card {
            background: rgba(30, 41, 59, 0.4);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            border: 1px solid rgba(255, 255, 255, 0.05);
            padding: 30px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4);
            margin-top: 25px;
        }
        
        /* High Contrast Typography */
        .movie-title-header { 
            font-size: 2.5rem; 
            font-weight: 900; 
            background: linear-gradient(to right, #FFFFFF, #94A3B8);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 15px; 
        }
        
        /* Badges */
        .badge {
            display: inline-block; padding: 6px 14px; border-radius: 8px;
            font-size: 0.85rem; font-weight: 700; margin-right: 10px; margin-bottom: 10px;
            text-transform: uppercase; letter-spacing: 0.5px;
        }
        .rating-badge { background-color: rgba(250, 204, 21, 0.1); color: #FACC15; border: 1px solid rgba(250, 204, 21, 0.2); }
        .date-badge { background-color: rgba(255, 255, 255, 0.05); color: #E2E8F0; border: 1px solid rgba(255, 255, 255, 0.1); }
        .runtime-badge { background-color: rgba(255, 255, 255, 0.05); color: #E2E8F0; border: 1px solid rgba(255, 255, 255, 0.1); }
        .genre-badge { background-color: rgba(99, 102, 241, 0.1); color: #818CF8; border: 1px solid rgba(99, 102, 241, 0.2); }
        
        /* Details Styling */
        .synopsis-text { color: #94A3B8; line-height: 1.8; font-size: 1.05rem; }
        .custom-divider { height: 1px; background: linear-gradient(to right, rgba(255,255,255,0.1), transparent); margin: 25px 0; }
        
        /* Movie Grid Cards */
        .grid-card {
            background: rgba(30, 41, 59, 0.5);
            backdrop-filter: blur(8px);
            border-radius: 16px;
            border: 1px solid rgba(255, 255, 255, 0.06);
            padding: 22px;
            transition: all 0.3s ease;
            height: 100%;
        }
        .grid-card:hover {
            border-color: rgba(99, 102, 241, 0.3);
            box-shadow: 0 8px 25px rgba(99, 102, 241, 0.15);
            transform: translateY(-2px);
        }
        .grid-card-title {
            font-size: 1.1rem;
            font-weight: 700;
            color: #FFFFFF;
            margin-bottom: 8px;
            line-height: 1.3;
        }
        .grid-card-year {
            font-size: 0.85rem;
            color: #64748B;
            margin-bottom: 12px;
        }
        .grid-card-rating {
            font-size: 1rem;
            color: #FACC15;
            font-weight: 700;
            margin-bottom: 10px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

def fetch_filtered_movies(filters):
    """Fetches movies from the deployed Google Cloud Function with advanced filtering."""
    cloud_function_url = 'https://getmovies-1031393311197.europe-west6.run.app/get_movies'
    
    try:
        response = requests.post(cloud_function_url, json=filters)
        response.raise_for_status()
        data = response.json()
        if isinstance(data, list):
            return data
        else:
            return data.get('results', [])
    except requests.RequestException as e:
        st.error(f"Erreur lors de la requête API: {e}")
        return []

def fetch_autocomplete(query, limit=5):
    """Fetches autocomplete suggestions for movie titles."""
    if not query or len(query) < 2:
        return []
    url = f"https://autocompletion-1031393311197.europe-west6.run.app/title_autocomplete?q={query}&limit={limit}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data.get('suggestions', [])
    except requests.RequestException:
        return []

@st.cache_data(ttl=3600)
def fetch_genres():
    """Fetches all available genres from the API."""
    url = "https://getgenres-1031393311197.europe-west6.run.app/get_genres"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data.get('genres', [])
    except requests.RequestException:
        return []

def fetch_tmdb_movie_details(movie_id):
    """Fetches full movie details directly from the TMDB API using the local API key."""
    api_key = os.getenv('TMB_apikey')
    if not api_key:
        st.error("API Key for TMDB is missing. Check your .env file.")
        return None

    url = f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}'
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        st.error(f"Error making TMDB API request: {e}")
        return None

def show_landing_page():
    apply_custom_styles()
    st.markdown(
        """
        <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 60vh; text-align: center;">
            <div style="background: rgba(99, 102, 241, 0.15); padding: 25px; border-radius: 100%; border: 1px solid rgba(99, 102, 241, 0.3); margin-bottom: 30px; box-shadow: 0 0 30px rgba(99, 102, 241, 0.2);">
                <span style="font-size: 50px;">☄️</span>
            </div>
            <h1 style="font-size: 4rem; font-weight: 900; background: linear-gradient(to bottom right, #FFFFFF, #6366F1); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 0;">CinéCloud</h1>
            <p style="font-size: 1.4rem; color: #94A3B8; max-width: 600px; margin-top: 20px; margin-bottom: 50px; font-weight: 500;">
                Plongez dans l'espace infini du cinéma. Recherche intelligente et expérience immersive.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        if st.button("🚀 Explorer la Galaxie", use_container_width=True):
            st.session_state.app_started = True
            st.rerun()

def main():
    apply_custom_styles()
    
    if "app_started" not in st.session_state:
        st.session_state.app_started = False
        
    if not st.session_state.app_started:
        show_landing_page()
        return
    
    # Si un film est sélectionné pour la fiche détaillée
    if "view_movie_id" in st.session_state:
        show_movie_detail_page(st.session_state.view_movie_id)
        return

    st.markdown('<h1 style="color: #FFFFFF; font-weight: 900; margin-bottom: 0.5rem; font-size: 2.5rem;">🌌 Catalogue Galactique</h1>', unsafe_allow_html=True)
    st.markdown('<p style="color: #94A3B8; font-size: 1.15rem; margin-bottom: 2.5rem; font-weight: 500;">Filtrage de précision et exploration profonde.</p>', unsafe_allow_html=True)
    
    col_search, col_sort = st.columns([3, 1], gap="medium")
    with col_search:
        title_prefix = st.text_input("Recherche de titre...", key="main_title_search", placeholder="Nom du film...", label_visibility="collapsed")
    with col_sort:
        tri = st.selectbox("Trier par", ["Titre A-Z", "Titre Z-A", "Année ↓", "Année ↑", "Note ↓", "Note ↑"], label_visibility="collapsed")
    
    if 'page' not in st.session_state:
        st.session_state.page = 1

    st.sidebar.markdown('<h2 style="font-size: 1.4rem; color: #FFFFFF; margin-bottom: 1.5rem;">⚙️ Paramètres</h2>', unsafe_allow_html=True)
    
    language = st.sidebar.selectbox("Langue", ["Toutes", "en", "fr", "es", "ja", "ko"])
    
    genres_list = fetch_genres()
    genre = st.sidebar.multiselect("Genre(s)", genres_list)
    min_avg_rating = st.sidebar.slider("Note minimale", min_value=0.0, max_value=5.0, value=0.0, step=0.5)
    released_after_year = st.sidebar.slider("Après l'année", min_value=1900, max_value=2026, value=1900, step=1)
    page_size = st.sidebar.selectbox("Résultats", [10, 20, 50, 100], index=0)
    
    payload = {"page": st.session_state.page, "page_size": page_size}
    if title_prefix: payload["title_prefix"] = title_prefix
    if language != "Toutes": payload["language"] = language
    if genre: payload["genre"] = "|".join(genre)
    if min_avg_rating > 0: payload["min_avg_rating"] = min_avg_rating
    if released_after_year > 1900: payload["released_after"] = released_after_year

    with st.spinner("Mise à jour de la bibliothèque..."):
         movies = fetch_filtered_movies(payload)
    
    if movies:
        if tri == "Titre A-Z":
            movies.sort(key=lambda m: m.get('title', '').lower())
        elif tri == "Titre Z-A":
            movies.sort(key=lambda m: m.get('title', '').lower(), reverse=True)
        elif tri == "Année ↓":
            movies.sort(key=lambda m: m.get('release_year', 0), reverse=True)
        elif tri == "Année ↑":
            movies.sort(key=lambda m: m.get('release_year', 9999))
        elif tri == "Note ↓":
            movies.sort(key=lambda m: m.get('avg_rating', 0), reverse=True)
        elif tri == "Note ↑":
            movies.sort(key=lambda m: m.get('avg_rating', 0))
        
        for idx, movie in enumerate(movies):
            title = movie.get('title', 'Sans titre')
            year = movie.get('release_year', '')
            genres = movie.get('genres', '')
            rating = movie.get('avg_rating', 0)
            tmdb_id = movie.get('tmdbId')
            
            genre_badges = ""
            if genres:
                for g in genres.split('|'):
                    genre_badges += f'<span class="badge genre-badge" style="font-size: 0.7rem; padding: 2px 8px; margin-bottom: 0;">{g.strip()}</span>'
            
            col_info, col_btn = st.columns([6, 1], gap="small")
            with col_info:
                st.markdown(f"""
                    <div class="grid-card" style="padding: 10px 18px; margin-bottom: -10px;">
                        <div style="display: flex; align-items: center; gap: 15px; flex-wrap: wrap;">
                            <div class="grid-card-title" style="margin-bottom: 0; font-size: 0.95rem;">{title}</div>
                            <span style="color: #64748B; font-size: 0.8rem;">{year}</span>
                            <span class="badge rating-badge" style="font-size: 0.75rem; padding: 2px 8px; margin-bottom: 0;">⭐ {round(rating, 1)}</span>
                            {genre_badges}
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            with col_btn:
                if tmdb_id:
                    if st.button("📖", key=f"btn_{tmdb_id}_{idx}", use_container_width=True):
                        st.session_state.view_movie_id = tmdb_id
                        st.rerun()
        
        # Pagination
        st.write("")
        col_prev, col_center, col_next = st.columns([1, 2, 1])
        with col_prev:
            if st.session_state.page > 1:
                if st.button("⬅️ Retour"):
                    st.session_state.page -= 1
                    st.rerun()
        with col_center:
            st.markdown(f'<p style="text-align: center; color: #94A3B8; font-size: 1rem; margin-top: 8px;">Page {st.session_state.page}</p>', unsafe_allow_html=True)
        with col_next:
            if len(movies) == page_size:
                if st.button("Suivant ➡️"):
                    st.session_state.page += 1
                    st.rerun()
    else:
        st.warning("Aucun film trouvé.")


def show_movie_detail_page(movie_id):
    """Affiche une page dédiée aux détails d'un film."""
    apply_custom_styles()
    
    if st.button("⬅️ Retour au catalogue"):
        del st.session_state.view_movie_id
        st.rerun()
    
    with st.spinner("Chargement de la fiche..."):
        tmdb_details = fetch_tmdb_movie_details(movie_id)
    
    if not tmdb_details:
        st.error("Impossible de charger les détails du film.")
        return
    
    st.markdown('<div class="movie-card">', unsafe_allow_html=True)
    
    col_poster, col_info = st.columns([1, 2], gap="large")
    
    with col_poster:
        if tmdb_details.get('poster_path'):
            poster_url = f"https://image.tmdb.org/t/p/w500{tmdb_details['poster_path']}"
            st.image(poster_url, width=350)
        else:
            st.info("Affiche non disponible")
    
    with col_info:
        st.markdown(f'<div class="movie-title-header">{tmdb_details.get("title", "Titre inconnu")}</div>', unsafe_allow_html=True)
        
        if tmdb_details.get('tagline'):
            st.markdown(f'<p style="color: #94A3B8; font-style: italic; font-size: 1.1rem; margin-bottom: 20px;">"{tmdb_details["tagline"]}"</p>', unsafe_allow_html=True)
        
        score = tmdb_details.get('vote_average', 'N/A')
        votes = tmdb_details.get('vote_count', 0)
        date = tmdb_details.get('release_date', 'N/A')
        runtime = tmdb_details.get('runtime', 'N/A')
        
        st.markdown(f"""
            <span class="badge rating-badge">⭐ {score}/10 ({votes} votes)</span>
            <span class="badge date-badge">📅 {date}</span>
            <span class="badge runtime-badge">⏱️ {runtime} min</span>
        """, unsafe_allow_html=True)
        
        genres_list = [g['name'] for g in tmdb_details.get('genres', [])]
        if genres_list:
            genres_html = "".join([f'<span class="badge genre-badge">{g}</span>' for g in genres_list])
            st.markdown(f"<div style='margin-top: 10px;'>{genres_html}</div>", unsafe_allow_html=True)
        
        st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
        st.markdown('<p style="color: #FFFFFF; font-weight: 700; margin-bottom: 10px; font-size: 1.1rem;">SYNOPSIS</p>', unsafe_allow_html=True)
        st.markdown(f'<div class="synopsis-text">{tmdb_details.get("overview", "Aucune description disponible.")}</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Infos complémentaires
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.markdown('<p style="color: #94A3B8; font-size: 0.9rem;">BUDGET</p>', unsafe_allow_html=True)
        budget = tmdb_details.get('budget', 0)
        st.markdown(f'<p style="color: #FFFFFF; font-size: 1.3rem; font-weight: 700;">${budget:,.0f}</p>' if budget else '<p style="color: #475569;">Non communiqué</p>', unsafe_allow_html=True)
    with col_b:
        st.markdown('<p style="color: #94A3B8; font-size: 0.9rem;">REVENUS</p>', unsafe_allow_html=True)
        revenue = tmdb_details.get('revenue', 0)
        st.markdown(f'<p style="color: #FFFFFF; font-size: 1.3rem; font-weight: 700;">${revenue:,.0f}</p>' if revenue else '<p style="color: #475569;">Non communiqué</p>', unsafe_allow_html=True)
    with col_c:
        st.markdown('<p style="color: #94A3B8; font-size: 0.9rem;">LANGUE ORIGINALE</p>', unsafe_allow_html=True)
        st.markdown(f'<p style="color: #FFFFFF; font-size: 1.3rem; font-weight: 700;">{tmdb_details.get("original_language", "N/A").upper()}</p>', unsafe_allow_html=True)


if __name__ == '__main__':
    main()
