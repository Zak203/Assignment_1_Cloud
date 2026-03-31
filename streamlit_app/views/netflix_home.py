import streamlit as st
import requests
import os
from api.elasticsearch_service import fetch_all_movies_dict
from api.services import fetch_genres, fetch_filtered_movies

ML_BACKEND_URL = os.getenv("ML_BACKEND_URL", "http://127.0.0.1:5001")
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
    m_id = movie_dict.get('movieId')
    if not m_id: return
    
    if "liked_movies_data" not in st.session_state:
        st.session_state.liked_movies_data = {}
        
    if m_id in st.session_state.liked_movies:
        st.session_state.liked_movies.remove(m_id)
        if m_id in st.session_state.liked_movies_data:
            del st.session_state.liked_movies_data[m_id]
        st.session_state.is_loading_like = True
        st.toast("🗑️ Film retiré de votre liste")
    else:
        # Fetch poster if missing (from catalog clicking)
        if not movie_dict.get("poster_url") and movie_dict.get("tmdbId"):
            movie_dict["poster_url"] = get_poster_url(movie_dict["tmdbId"])
            
        st.session_state.liked_movies.add(m_id)
        st.session_state.liked_movies_data[m_id] = movie_dict
        st.session_state.is_loading_like = True
        st.toast("❤️ Film ajouté à votre liste !")

def view_details(tmdb_id):
    st.session_state.view_movie_id = tmdb_id

def fetch_popular_movies(top_n=150):
    try:
        resp = requests.get(f"{ML_BACKEND_URL}/movies/popular?top_n={top_n}&posters=false", timeout=10)
        resp.raise_for_status()
        return resp.json().get("results", [])
    except:
        return []

def fetch_recommendations(movie_ids, top_n=150):
    try:
        resp = requests.post(f"{ML_BACKEND_URL}/recommend", json={"movie_ids": list(movie_ids), "top_n": top_n, "posters": False}, timeout=30)
        resp.raise_for_status()
        return resp.json().get("results", [])
    except:
        return []

def apply_ml_filters(movies, genres, min_rating, min_year, target_language, movies_dict):
    if not movies: return []
    filtered = []
    import re
    
    # ML Backend rating is normalized 0-1, whereas min_rating is 0-5.
    min_ml_score = min_rating / 5.0
    
    for m in movies:
        # Genre filter
        if genres:
            m_genres = set(m.get('genres', '').split('|'))
            if not any(g in m_genres for g in genres):
                continue
                
        # Rating filter
        r = m.get('score') or m.get('avg_rating', 0)
        if min_rating > 0 and r < min_ml_score:
            continue
            
        # Year filter (extracted from title '... (1999)')
        if min_year > 1900:
            match = re.search(r'\((\d{4})\)', m.get('title', ''))
            year = int(match.group(1)) if match else 0
            if year < min_year:
                continue
                
        # Language filter (using Elasticsearch mapping)
        if target_language:
            info = movies_dict.get(m.get('title'), {})
            if info.get('language') != target_language:
                continue
                
        filtered.append(m)
    return filtered

def render_unified_movie_gallery(title, items, is_objects=False, salt="", movies_dict=None):
    """Render a 5-column gallery layout (Grid) for all views."""
    if not items: return
    import re
    
    st.markdown(f"<div class='row-title' style='margin-bottom: 16px; margin-top: 20px;'>{title}</div>", unsafe_allow_html=True)
    display_items = items[:20] if not is_objects else items
    
    # Process all posters sequentially to avoid API spam if needed
    for m in display_items:
        tmdb_id = m.tmdb_id if is_objects else (m.get("tmdbId") or (movies_dict.get(m.get("title", ""), {}) if getattr(m, 'get', None) else {}).get("tmdbId"))
        poster_url = None if is_objects else m.get("poster_url")
        if not poster_url and tmdb_id:
            if is_objects: m.poster_url = get_poster_url(tmdb_id)
            else: m["poster_url"] = get_poster_url(tmdb_id)

    cols = st.columns(5)
    for idx, item in enumerate(display_items):
        with cols[idx % 5]:
            if is_objects:
                title_str = item.title
                rating = round(item.avg_rating, 1) if item.avg_rating else 0
                tmdb_id = item.tmdb_id
                m_ml_id = movies_dict.get(title_str, {}).get("movieId") if movies_dict else None
                ml_score = None
                poster_url = getattr(item, 'poster_url', None)
            else:
                title_str = item.get("title", "")
                info = movies_dict.get(title_str, {}) if movies_dict else {}
                rating = round(item.get("avg_rating", 0), 1) if item.get("avg_rating") else 0
                tmdb_id = item.get("tmdbId") or info.get("tmdbId")
                m_ml_id = item.get("movieId") or info.get("movieId")
                ml_score = round(float(item.get("score")), 2) if item.get("score") else None
                poster_url = item.get("poster_url")

            st.markdown("<div class='movie-card-container'>", unsafe_allow_html=True)
            if poster_url:
                st.markdown(f"<img src='{poster_url}' style='width:100%; aspect-ratio:2/3; object-fit:cover; border-radius:6px; box-shadow:0 4px 10px rgba(0,0,0,0.5);'>", unsafe_allow_html=True)
            else:
                st.markdown("<div style='width:100%; aspect-ratio:2/3; background:#222; border-radius:6px; display:flex; align-items:center; justify-content:center; border:1px solid #333;'><span style='color:#666;'>Pas d'image</span></div>", unsafe_allow_html=True)
                
            st.markdown(f"<div class='movie-info'><div class='movie-title'>{title_str}</div>", unsafe_allow_html=True)
            if ml_score:
                st.markdown(f"<div class='movie-meta' style='color: #46d369; font-weight: bold;'>🎯 IA: {ml_score}</div>", unsafe_allow_html=True)
            elif rating:
                st.markdown(f"<div class='movie-meta'>⭐ {rating} / 5</div>", unsafe_allow_html=True)
            st.markdown("</div></div>", unsafe_allow_html=True)
            
            c1, c2 = st.columns([1, 1])
            with c1:
                if m_ml_id:
                    is_liked = m_ml_id in st.session_state.get("liked_movies", set())
                    lbl = "❌" if is_liked else "🤍"
                    fake_dict = {"movieId": m_ml_id, "title": title_str, "tmdbId": tmdb_id, "poster_url": poster_url}
                    st.button(lbl, key=f"gal_like_{salt}_{idx}_{m_ml_id}", on_click=toggle_like, args=(fake_dict,), type="secondary")
            with c2:
                if tmdb_id:
                    st.button("📖", key=f"gal_det_{salt}_{idx}_{tmdb_id}", on_click=view_details, args=(tmdb_id,), type="secondary")
            st.write("")

def show_netflix_home():
    if "liked_movies" not in st.session_state:
        st.session_state.liked_movies = set()
        st.session_state.liked_movies_data = {}
    if 'page' not in st.session_state:
        st.session_state.page = 1

    if st.session_state.get('is_loading_like', False):
        st.session_state.is_loading_like = False
        with st.spinner("L'IA recalcule vos recommandations..."):
            import time
            time.sleep(1.0)

    movies_dict = fetch_all_movies_dict()

    st.markdown("""
    <style>
    .block-container { padding-top: 0.5rem !important; padding-bottom: 0 !important; }

    /* NAV BUTTONS ONLY: text-only underlined style (scoped via parent id) */
    #nav-row button {
        background-color: transparent !important; border: none !important;
        font-size: 0.95rem !important; padding: 0 0 2px 0 !important;
        box-shadow: none !important; border-radius: 0 !important;
        text-transform: uppercase !important; color: #b3b3b3 !important; font-weight: 500 !important;
    }
    #nav-row button:hover { color: #ffffff !important; }
    #nav-row button[kind="primary"] {
        color: #ffffff !important; font-weight: 700 !important;
        border-bottom: 2px solid #E50914 !important;
    }

    /* Strip ALL select/multiselect input borders globally */
    div[data-baseweb="select"] > div,
    div[data-baseweb="select"] > div > div {
        background-color: transparent !important; border: none !important;
        border-bottom: 1px solid #444 !important; border-radius: 0 !important;
        color: #fff !important; padding: 0 !important; min-height: 28px !important;
        box-shadow: none !important;
    }
    div[data-baseweb="select"]:hover > div { border-bottom: 1px solid #E50914 !important; }
    /* Strip multiselect tag pills */
    span[data-baseweb="tag"] { background-color: #333 !important; border: none !important; }

    /* Gallery cards */
    .movie-card-container { margin-bottom: 20px; transition: transform 0.2s; }
    .movie-card-container:hover { transform: scale(1.03); }
    .movie-info { padding-top: 6px; }
    .movie-title { font-size: 0.85rem; font-weight: 700; color: #fff; line-height: 1.2; text-overflow: ellipsis; overflow: hidden; white-space: nowrap; }
    .movie-meta { font-size: 0.75rem; color: #aaa; margin-top: 2px; }

    /* Trending banner – infinite scroll */
    @keyframes scrollBanner {
        0% { transform: translateX(0); }
        100% { transform: translateX(-50%); }
    }
    .banner-track {
        display: flex; gap: 16px;
        animation: scrollBanner 40s linear infinite;
        width: max-content;
    }
    .banner-card {
        flex-shrink: 0; width: 200px; position: relative; border-radius: 8px; overflow: hidden;
        box-shadow: 0 6px 20px rgba(0,0,0,0.6);
    }
    .banner-card img { width: 200px; height: 300px; object-fit: cover; display: block; }
    .banner-card .overlay {
        position: absolute; bottom: 0; left: 0; right: 0; padding: 10px;
        background: linear-gradient(transparent, rgba(0,0,0,0.85));
    }
    .banner-card .overlay .b-title { font-size: 0.8rem; font-weight: 700; color: #fff; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    .banner-card .overlay .b-score { font-size: 0.7rem; color: #46d369; font-weight: 600; }
    </style>
    """, unsafe_allow_html=True)

    # ROW 1: Title + Filters
    col_t, col_lang, col_genre, col_rat, col_yr = st.columns([3.5, 1.2, 1.2, 1, 1])
    with col_t:
        st.markdown("<h1 style='color:#E50914 !important; font-size:2rem; margin:0; letter-spacing:-1px; text-transform:uppercase;'>Netflix UNIL</h1>", unsafe_allow_html=True)
    with col_lang:
        lang_options = {"Langue": None, "Anglais": "en", "Français": "fr", "Espagnol": "es", "Japonais": "ja", "Coréen": "ko"}
        language_label = st.selectbox("Langue", list(lang_options.keys()), label_visibility="collapsed")
    with col_genre:
        genres_list = fetch_genres()
        genre = st.multiselect("Genre(s)", genres_list, placeholder="Genre", label_visibility="collapsed")
    with col_rat:
        min_avg_rating = st.selectbox("Note", [0.0, 1.0, 2.0, 3.0, 4.0, 4.5], format_func=lambda x: f"Note ≥ {x}" if x > 0 else "Note", label_visibility="collapsed")
    with col_yr:
        released_after_year = st.selectbox("Année", [1900, 1980, 1990, 2000, 2010, 2020], format_func=lambda x: f"≥ {x}" if x > 1900 else "Année", label_visibility="collapsed")

    # ROW 2: Search Icon + Navigation Tabs
    if "current_tab" not in st.session_state:
        st.session_state.current_tab = "Accueil"
    def set_tab(t): st.session_state.current_tab = t

    all_titles = sorted(list(movies_dict.keys()))
    if "search_widget" not in st.session_state: st.session_state.search_widget = ""
    def on_search_selected():
        info = movies_dict.get(st.session_state.search_widget)
        if info and info.get("tmdbId"):
            st.session_state.search_widget = ""
            view_details(info["tmdbId"])

    n_favs = len(st.session_state.get('liked_movies', set()))

    st.markdown("<div id='nav-row'>", unsafe_allow_html=True)
    c_s, c1, c2, c3, c4 = st.columns([1.5, 1, 2, 2, 1.8])
    with c_s:
        st.selectbox("🔍", ["🔍 Rechercher..."] + all_titles, key="search_widget", on_change=on_search_selected, label_visibility="collapsed")
    with c1:
        st.button("Accueil", key="nav_home", on_click=set_tab, args=("Accueil",), type="primary" if st.session_state.current_tab == "Accueil" else "secondary")
    with c2:
        st.button("Recommandations", key="nav_rec", on_click=set_tab, args=("Recommandations",), type="primary" if st.session_state.current_tab == "Recommandations" else "secondary")
    with c3:
        st.button("Catalogue Complet", key="nav_cat", on_click=set_tab, args=("Catalogue Complet",), type="primary" if st.session_state.current_tab == "Catalogue Complet" else "secondary")
    with c4:
        st.button(f"Favoris ({n_favs})", key="nav_fav", on_click=set_tab, args=("Mes Favoris",), type="primary" if st.session_state.current_tab == "Mes Favoris" else "secondary")
    st.markdown("</div>", unsafe_allow_html=True)

    current_tab = st.session_state.current_tab
    target_language = lang_options[language_label]
    page_size = 20

    st.markdown("<hr style='border-color:#333; margin:5px 0 15px 0;'>", unsafe_allow_html=True)

    # === CONTENT ===
    if current_tab == "Accueil":
        with st.spinner("Chargement des tendances..."):
            popular_movies = fetch_popular_movies(top_n=30)
            popular_movies = apply_ml_filters(popular_movies, genre, float(min_avg_rating), int(released_after_year), target_language, movies_dict)

            import re as _re
            banner_cards = ""
            for m in popular_movies[:20]:
                tmdb_id = m.get("tmdbId")
                if not m.get("poster_url") and tmdb_id:
                    m["poster_url"] = get_poster_url(tmdb_id)
                if m.get("poster_url"):
                    t = m.get('title', '')
                    sc = m.get('avg_rating', 0)
                    sc_txt = f"<div class='b-score'>⭐ {round(sc, 1)}</div>" if sc else ""
                    banner_cards += f"<div class='banner-card'><img src='{m['poster_url']}'><div class='overlay'><div class='b-title'>{t}</div>{sc_txt}</div></div>"

            if banner_cards:
                # Duplicate cards for seamless infinite loop
                st.markdown("🔥 <span style='font-size:1.5rem; font-weight:700; color:#fff;'>Tendances Actuelles</span>", unsafe_allow_html=True)
                st.markdown(f"<div style='overflow:hidden; padding:10px 0;'><div class='banner-track'>{banner_cards}{banner_cards}</div></div>", unsafe_allow_html=True)

        if len(st.session_state.liked_movies) > 0:
            with st.spinner("L'IA analyse vos goûts..."):
                recommendations = fetch_recommendations(st.session_state.liked_movies, top_n=20)
                recommendations = apply_ml_filters(recommendations, genre, float(min_avg_rating), int(released_after_year), target_language, movies_dict)
            if recommendations:
                render_unified_movie_gallery("✨ Recommandé pour vous", recommendations, salt="rec_preview", movies_dict=movies_dict)

    elif current_tab == "Recommandations":
        if len(st.session_state.liked_movies) > 0:
            with st.spinner("L'IA calcule vos recommandations personnalisées..."):
                recommendations = fetch_recommendations(st.session_state.liked_movies, top_n=100)
                recommendations = apply_ml_filters(recommendations, genre, float(min_avg_rating), int(released_after_year), target_language, movies_dict)
            if recommendations:
                render_unified_movie_gallery("🎯 Vos Coups de Cœur", recommendations, salt="rec_full", movies_dict=movies_dict)
            else:
                st.info("Aucune recommandation ne correspond à vos filtres.")
        else:
            st.info("💡 Likez quelques films pour activer l'IA ! En attendant, voici les tendances (Cold Start) :")
            with st.spinner("Chargement..."):
                popular_movies = fetch_popular_movies(top_n=30)
                popular_movies = apply_ml_filters(popular_movies, genre, float(min_avg_rating), int(released_after_year), target_language, movies_dict)
                render_unified_movie_gallery("🔥 Sélection Découverte", popular_movies, salt="cold", movies_dict=movies_dict)

    elif current_tab == "Mes Favoris":
        if len(st.session_state.liked_movies) > 0:
            liked_list = list(st.session_state.liked_movies_data.values())
            liked_list = apply_ml_filters(liked_list, genre, float(min_avg_rating), int(released_after_year), target_language, movies_dict)
            if liked_list:
                render_unified_movie_gallery("🤍 Mes Favoris", liked_list[::-1], salt="fav", movies_dict=movies_dict)
            else:
                st.info("Aucun favori ne correspond à ces filtres.")
        else:
            st.info("Votre liste de favoris est vide.")

    elif current_tab == "Catalogue Complet":
        payload = {"page": st.session_state.page, "page_size": page_size}
        if lang_options[language_label]: payload["language"] = lang_options[language_label]
        if genre: payload["genre"] = "|".join(genre)
        if float(min_avg_rating) > 0: payload["min_avg_rating"] = float(min_avg_rating)
        if int(released_after_year) > 1900: payload["released_after"] = int(released_after_year)

        with st.spinner("Chargement du catalogue..."):
            catalog_movies = fetch_filtered_movies(payload)

        if catalog_movies:
            render_unified_movie_gallery("🎬 Catalogue complet", catalog_movies, is_objects=True, salt="cat", movies_dict=movies_dict)
            col_prev, col_center, col_next = st.columns([1, 2, 1])
            with col_prev:
                if st.session_state.page > 1:
                    if st.button("⬅️ Retour", key="btn_prev"):
                        st.session_state.page -= 1
                        st.rerun()
            with col_center:
                st.markdown(f'<p style="text-align:center; color:#aaa; margin-top:8px;">Page {st.session_state.page}</p>', unsafe_allow_html=True)
            with col_next:
                if len(catalog_movies) == page_size:
                    if st.button("Suivant ➡️", key="btn_next"):
                        st.session_state.page += 1
                        st.rerun()
        else:
            st.info("Aucun film ne correspond à vos filtres.")
