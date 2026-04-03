import streamlit as st
import requests
import os
import re
from api.elasticsearch_service import fetch_all_movies_dict, fetch_total_movie_count
from api.services import fetch_genres, fetch_filtered_movies
from ui.interactions import toggle_like, get_poster_url

ML_BACKEND_URL = os.getenv("ML_BACKEND_URL", "http://127.0.0.1:5001")

def fix_title(raw_title):
    """Supprime l'année et corrige les articles inversés : 'Matrix, The (1999)' → 'The Matrix'"""
    t = re.sub(r'\s*\(\d{4}\)\s*$', '', raw_title).strip()
    m = re.match(r'^(.*),\s*(The|A|An|Les|Le|La|Une|Un|Der|Die|Das|El|Los|Las)$', t, re.IGNORECASE)
    if m:
        article = m.group(2)
        article = article[0].upper() + article[1:].lower()
        return f"{article} {m.group(1).strip()}"
    return t

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
    min_ml_score = min_rating / 5.0
    for m in movies:
        if genres:
            m_genres = set(m.get('genres', '').split('|'))
            if not any(g in m_genres for g in genres):
                continue
        r = m.get('score') or m.get('avg_rating', 0)
        if min_rating > 0 and r < min_ml_score:
            continue
        if min_year > 1900:
            # Ancré en fin de chaîne pour éviter de matcher un chiffre au milieu du titre
            # ex: "Mission 2020 (1981)" → on veut 1981, pas 2020
            raw_title = m.get('title') or ''
            match = re.search(r'\((\d{4})\)\s*$', raw_title)
            year = int(match.group(1)) if match else 0
            if year < min_year:
                continue
        if target_language:
            info = movies_dict.get(m.get('title'), {})
            if info.get('language') != target_language:
                continue
        filtered.append(m)
    return filtered

def render_unified_movie_gallery(title, items, is_objects=False, salt="", movies_dict=None):
    if not items: return
    
    st.markdown(f"<div class='row-title' style='margin-bottom: 16px; margin-top: 20px; font-weight: bold; color:white;'>{title}</div>", unsafe_allow_html=True)
    display_items = items[:20] if not is_objects else items
    
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
                genres_raw = getattr(item, 'genres', '') or movies_dict.get(title_str, {}).get('genres', '')
                lang = getattr(item, 'language', '') or movies_dict.get(title_str, {}).get('language', '')
            else:
                title_str = item.get("title", "")
                info = movies_dict.get(title_str, {}) if movies_dict else {}
                # avg_rating de BigQuery est sur échelle 0-1 (rating_im) → convertir en /5
                raw_avg = item.get("avg_rating", 0) or 0
                rating = round(raw_avg * 5, 1) if raw_avg else 0
                tmdb_id = item.get("tmdbId") or info.get("tmdbId")
                m_ml_id = item.get("movieId") or info.get("movieId")
                # score IA BigQuery est sur 0-1 → afficher en %
                ml_score = round(float(item.get("score")) * 100) if item.get("score") else None
                poster_url = item.get("poster_url")
                genres_raw = item.get('genres', '') or info.get('genres', '')
                lang = item.get('language', '') or info.get('language', '')

            clean_t = fix_title(title_str)
            ym = re.search(r'\((\d{4})\)', title_str)
            year = ym.group(1) if ym else ''
            genres_disp = ' · '.join([g.strip() for g in (genres_raw.split('|') if isinstance(genres_raw, str) else []) if g.strip()][:2]) if genres_raw else ''
            lang_str = lang.upper() if isinstance(lang, str) and lang else ''
            
            st.markdown("<div class='movie-card-container'>", unsafe_allow_html=True)
            if poster_url:
                st.markdown(f"<img src='{poster_url}' style='width:100%; aspect-ratio:2/3; object-fit:cover; border-radius:6px; box-shadow:0 4px 10px rgba(0,0,0,0.5);'>", unsafe_allow_html=True)
            else:
                st.markdown("<div style='width:100%; aspect-ratio:2/3; background:#222; border-radius:6px; display:flex; align-items:center; justify-content:center; border:1px solid #333;'><span style='color:#666;'>Pas d'image</span></div>", unsafe_allow_html=True)
                
            st.markdown(f"<div class='movie-info'><div class='movie-title'>{clean_t}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='movie-meta'>{year}{' • ' + lang_str if lang_str else ''}<br>{genres_disp}</div>", unsafe_allow_html=True)
            if ml_score:
                st.markdown(f"<div class='movie-meta' style='color: #46d369; font-weight: bold; margin-top:2px;'>🎯 Score IA : {ml_score}%</div>", unsafe_allow_html=True)
            if rating:
                st.markdown(f"<div class='movie-meta' style='margin-top:2px;'>⭐ {rating} / 5</div>", unsafe_allow_html=True)
            st.markdown("</div></div>", unsafe_allow_html=True)
            
            c1, c2 = st.columns([1, 1])
            with c1:
                if m_ml_id:
                    is_liked = m_ml_id in st.session_state.get("liked_movies", set())
                    lbl = "❌ Retirer" if is_liked else "🤍 Liker"
                    fake_dict = {"movieId": m_ml_id, "title": title_str, "tmdbId": tmdb_id, "poster_url": poster_url}
                    st.button(lbl, key=f"gal_like_{salt}_{idx}_{m_ml_id}", on_click=toggle_like, args=(fake_dict,), use_container_width=True)
            with c2:
                if tmdb_id:
                    st.button("▶ Détails", key=f"gal_det_{salt}_{idx}_{tmdb_id}", on_click=view_details, args=(tmdb_id,), type="primary", use_container_width=True)
            st.write("")

def show_netflix_home():
    movies_dict = fetch_all_movies_dict()
    all_titles = sorted(list(movies_dict.keys()))
    total_movie_count = fetch_total_movie_count()

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

    st.markdown("""
    <style>
    /* === MASSIVE TOP RED GRADIENT BAR === */
    .stApp::before {
        content: '';
        position: fixed;
        top: 0; left: 0; right: 0;
        height: 3px;
        background: linear-gradient(90deg, transparent 0%, #E50914 25%, #ff2d3a 50%, #E50914 75%, transparent 100%);
        z-index: 9999;
    }
    
    .block-container { padding-top: 0.5rem !important; padding-bottom: 0 !important; }
    
    /* === NETFLIX TEXT GRADIENT === */
    .nf-title-wrap { display: flex; align-items: baseline; gap: 0; padding: 6px 0 10px 0; line-height: 1; }
    .nf-title-netflix {
        font-size: 2.8rem; font-weight: 900; letter-spacing: -1.5px;
        background: linear-gradient(145deg, #ff1a24 0%, #E50914 40%, #c20810 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        text-transform: uppercase; filter: drop-shadow(0 2px 12px rgba(229,9,20,0.35));
    }
    .nf-title-unil { font-size: 2.8rem; font-weight: 200; letter-spacing: 10px; color: #fff; margin-left: 10px; text-transform: uppercase; }

    /* === NAVIGATION BUTTONS AS PURE TEXT === */
    [data-testid="stHorizontalBlock"] button {
        background-color: transparent !important; 
        border: none !important;
        font-size: 1.05rem !important;
        box-shadow: none !important;
        color: #b3b3b3 !important; 
        font-weight: 600 !important;
        padding-left: 0 !important;
        padding-right: 0 !important;
    }
    [data-testid="stHorizontalBlock"] button:hover { color: #ffffff !important; }
    [data-testid="stHorizontalBlock"] button[kind="primary"] {
        color: #E50914 !important; 
        font-weight: 800 !important;
        border-bottom: 3px solid #E50914 !important;
        border-radius: 0 !important;
    }

    /* === ULTRA CLEAN PRO FILTERS === */
    div[data-baseweb="select"] {
        min-width: 100% !important;
    }

    div[data-baseweb="select"] > div {
        background: transparent !important;
        border: none !important;
        border-bottom: 1px solid rgba(255,255,255,0.14) !important;
        border-radius: 0 !important;
        box-shadow: none !important;
        min-height: 42px !important;
        padding-left: 0 !important;
        padding-right: 0 !important;
        transition: border-color 0.18s ease, background-color 0.18s ease;
    }

    div[data-baseweb="select"] > div:hover {
        background: transparent !important;
        border-bottom: 1px solid rgba(255,255,255,0.35) !important;
    }

    div[data-baseweb="select"] > div:focus-within {
        background: transparent !important;
        border-bottom: 1px solid #E50914 !important;
        box-shadow: none !important;
    }

    /* Texte affiché */
    div[data-baseweb="select"] span,
    div[data-baseweb="select"] input,
    div[data-baseweb="select"] div {
        color: #f5f5f5 !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        letter-spacing: 0.2px !important;
    }

    /* Placeholder */
    div[data-baseweb="select"] input::placeholder {
        color: #9f9f9f !important;
        opacity: 1 !important;
    }

    /* Icône dropdown discrète */
    div[data-baseweb="select"] svg {
        display: inline-block !important;
        color: #8a8a8a !important;
        width: 16px !important;
        height: 16px !important;
    }

    /* Supprime les séparateurs internes bizarres */
    div[data-baseweb="select"] * {
        box-shadow: none !important;
    }

    /* Multi-select tags ultra propres */
    span[data-baseweb="tag"] {
        background: rgba(255,255,255,0.06) !important;
        border: 1px solid rgba(255,255,255,0.12) !important;
        border-radius: 999px !important;
        padding: 2px 8px !important;
    }

    span[data-baseweb="tag"] span {
        color: #f2f2f2 !important;
        font-weight: 500 !important;
        font-size: 0.85rem !important;
    }

    span[data-baseweb="tag"] svg {
        color: #cfcfcf !important;
        width: 12px !important;
        height: 12px !important;
    }

    /* Menu déroulant */
    ul[role="listbox"] {
        background: #111 !important;
        border: 1px solid rgba(255,255,255,0.08) !important;
        border-radius: 10px !important;
        box-shadow: 0 10px 30px rgba(0,0,0,0.45) !important;
    }

    ul[role="listbox"] li {
        color: #f1f1f1 !important;
        font-weight: 500 !important;
        background: transparent !important;
    }

    ul[role="listbox"] li:hover {
        background: rgba(229,9,20,0.12) !important;
    }

    ul[role="listbox"] li[aria-selected="true"] {
        background: rgba(229,9,20,0.18) !important;
        color: #fff !important;
    }
    
    /* Multiselect Tags (Genres) */
    span[data-baseweb="tag"] {
        background-color: rgba(229,9,20,0.2) !important;
        border: 1px solid rgba(229,9,20,0.5) !important;
        color: #fff !important;
        border-radius: 4px !important;
    }
    span[data-baseweb="tag"] span { color: #fff !important; font-weight: 600 !important; }
    span[data-baseweb="tag"] svg { color: #fff !important; display: inline-block !important; width:12px !important; height:12px !important; }

    /* === MOVIES DISPLAY === */
    .movie-card-container { margin-bottom: 20px; transition: transform 0.2s; }
    .movie-card-container:hover { transform: scale(1.03); }
    .movie-info { padding-top: 6px; }
    .movie-title { font-size: 0.85rem; font-weight: 700; color: #fff; line-height: 1.2; text-overflow: ellipsis; overflow: hidden; white-space: nowrap; }
    .movie-meta { font-size: 0.75rem; color: #aaa; margin-top: 2px; }
    
    /* === BADGE PULSANT RECOMMANDATIONS === */
    @keyframes pulseRec { 0%,100%{opacity:1;transform:scale(1)} 50%{opacity:0.5;transform:scale(0.75)} }
    .reco-new-badge {
        display: block;
        font-size: 0.6rem;
        color: #E50914;
        font-weight: 700;
        letter-spacing: 0.05em;
        text-align: center;
        margin-top: -10px;
        animation: pulseRec 1.2s ease-in-out infinite;
    }

    /* === LARGE MOVIE CARDS FOR TRENDING === */
    .large-movie-container { margin-bottom: 30px; transition: transform 0.2s; position: relative;}
    .large-movie-container:hover { transform: scale(1.02); }
    .large-movie-info { padding-top: 10px; }
    .large-movie-title { font-size: 1.2rem; font-weight: 800; color: #fff; line-height: 1.3; text-overflow: ellipsis; overflow: hidden; white-space: nowrap; }
    .large-movie-meta { font-size: 0.9rem; color: #ccc; margin-top: 4px; font-weight: 600;}
    .large-movie-score { font-size: 1rem; color: #46d369; font-weight: 700; margin-top: 2px;}
    </style>
    """, unsafe_allow_html=True)

    # ROW 1: Title + Filters
    col_t, col_lang, col_genre, col_rat, col_yr = st.columns([3.5, 1.2, 1.2, 1, 1])
    with col_t:
        st.markdown(
            "<div class='nf-title-wrap'>"
            "<span class='nf-title-netflix'>Netflix</span>"
            "<span class='nf-title-unil'>UNIL</span>"
            "</div>", unsafe_allow_html=True
        )
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

    # ROW 2: Navigation and huge Search Bar
    if "current_tab" not in st.session_state:
        st.session_state.current_tab = "Accueil"
    def set_tab(t): st.session_state.current_tab = t

    n_favs = len(st.session_state.get('liked_movies', set()))

    # Make the search bar column much bigger (c_s = 4.5)
    c1, c2, c3, c4, c_s = st.columns([1.5, 2.5, 2.5, 1.5, 4.5])
    with c1:
        st.button("Accueil", key="nav_home", on_click=set_tab, args=("Accueil",), type="primary" if st.session_state.current_tab == "Accueil" else "secondary")
    with c2:
        st.button("Recommandations", key="nav_rec", on_click=set_tab, args=("Recommandations",), type="primary" if st.session_state.current_tab == "Recommandations" else "secondary")
        if n_favs > 0 and st.session_state.current_tab != "Recommandations":
            st.markdown("<span class='reco-new-badge'>● nouvelles recos</span>", unsafe_allow_html=True)
    with c3:
        st.button("Catalogue Complet", key="nav_cat", on_click=set_tab, args=("Catalogue Complet",), type="primary" if st.session_state.current_tab == "Catalogue Complet" else "secondary")
    with c4:
        st.button(f"Favoris ({n_favs})", key="nav_fav", on_click=set_tab, args=("Mes Favoris",), type="primary" if st.session_state.current_tab == "Mes Favoris" else "secondary")
    
    def handle_search():
        val = st.session_state.live_search
        if val and val != "🔍 Chercher un film...":
            info = movies_dict.get(val)
            if info and info.get("tmdbId"):
                st.session_state.view_movie_id = info["tmdbId"]
            st.session_state.live_search = "🔍 Chercher un film..."

    with c_s:
        st.selectbox("🔍", ["🔍 Chercher un film..."] + all_titles, key="live_search", label_visibility="collapsed", on_change=handle_search)

    current_tab = st.session_state.current_tab
    target_language = lang_options[language_label]
    page_size = 20

    st.markdown("<hr style='border-color:#333; margin:10px 0 25px 0;'>", unsafe_allow_html=True)

    # === CONTENT ===
    if current_tab == "Accueil":
        with st.spinner("Chargement des tendances..."):
            popular_movies = fetch_popular_movies(top_n=30)
            popular_movies = apply_ml_filters(popular_movies, genre, float(min_avg_rating), int(released_after_year), target_language, movies_dict)

            st.markdown(f"<div style='text-align:right; font-size:0.75rem; color:#555; margin-bottom:-25px;'>🍿 Catalogue complet : <b>{total_movie_count:,}</b> | 🎯 Indexés IA (BigQuery) : <b>{len(all_titles)}</b></div>", unsafe_allow_html=True)
            st.markdown("🔥 <span style='font-size:1.8rem; font-weight:800; color:#fff;'>Tendances Actuelles</span>", unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Using 4 large columns for huge posters natively!
            num_cols = 4
            top_popular = popular_movies[:12] # show 12 huge movies
            rows = [top_popular[i:i + num_cols] for i in range(0, len(top_popular), num_cols)]
            
            for row_idx, row in enumerate(rows):
                cols = st.columns(num_cols)
                for i, m in enumerate(row):
                    with cols[i]:
                        tmdb_id = m.get("tmdbId")
                        if not m.get("poster_url") and tmdb_id:
                            m["poster_url"] = get_poster_url(tmdb_id)
                        
                        t = m.get('title', '')
                        clean_t = fix_title(t)
                        ym = re.search(r'\((\d{4})\)', t)
                        year = ym.group(1) if ym else ''
                        genres_raw = m.get('genres', '') or ''
                        genres_disp = ' · '.join([g.strip() for g in genres_raw.split('|') if g.strip()][:2])
                        sc = m.get('avg_rating', 0) or 0
                        # avg_rating BQ est sur 0-1 (rating_im) → convertir en /5
                        sc_txt = f"⭐ {round(sc * 5, 1)} / 5" if sc else ""
                        
                        m_ml_id = m.get("movieId")
                        if not m_ml_id:
                             info = movies_dict.get(t, {})
                             m_ml_id = info.get("movieId")

                        st.markdown("<div class='large-movie-container'>", unsafe_allow_html=True)
                        if m.get('poster_url'):
                            st.markdown(f"<img src='{m['poster_url']}' style='width:100%; aspect-ratio:2/3; object-fit:cover; border-radius:10px; box-shadow:0 10px 30px rgba(0,0,0,0.6);'>", unsafe_allow_html=True)
                        else:
                            st.markdown("<div style='width:100%; aspect-ratio:2/3; background:#222; border-radius:10px; border:1px solid #333;'></div>", unsafe_allow_html=True)
                        
                        st.markdown(f"<div class='large-movie-info'><div class='large-movie-title'>{clean_t}</div>", unsafe_allow_html=True)
                        st.markdown(f"<div class='large-movie-meta'>{year} • {genres_disp}</div>", unsafe_allow_html=True)
                        st.markdown(f"<div class='large-movie-score'>{sc_txt}</div></div></div>", unsafe_allow_html=True)

                        btn_col1, btn_col2 = st.columns([1, 1])
                        with btn_col1:
                            if m_ml_id:
                                is_liked = m_ml_id in st.session_state.get("liked_movies", set())
                                heart_icon = "❌ Retirer" if is_liked else "🤍 Liker"
                                fake_dict = {"movieId": m_ml_id, "title": t, "tmdbId": tmdb_id, "poster_url": m.get('poster_url')}
                                st.button(heart_icon, key=f"big_like_{row_idx}_{i}_{m_ml_id}", on_click=toggle_like, args=(fake_dict,), use_container_width=True)
                        with btn_col2:
                            if tmdb_id:
                                st.button("▶ Détails", key=f"big_det_{row_idx}_{i}_{tmdb_id}", on_click=view_details, args=(tmdb_id,), type="primary", use_container_width=True)
                        st.markdown("<br><br>", unsafe_allow_html=True)

    elif current_tab == "Recommandations":
        st.markdown(f"<div style='text-align:right; font-size:0.75rem; color:#555; margin-bottom:-25px;'>🎯 Indexés IA (BigQuery) : <b>{len(all_titles)}</b></div>", unsafe_allow_html=True)
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
        st.markdown(f"<div style='text-align:right; font-size:0.75rem; color:#555; margin-bottom:-25px;'>🎯 Indexés IA (BigQuery) : <b>{len(all_titles)}</b></div>", unsafe_allow_html=True)
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
            st.markdown(f"<div style='text-align:right; font-size:0.75rem; color:#555; margin-bottom:-20px;'>🍿 Catalogue complet : <b>{total_movie_count:,}</b> | 🎯 Indexés IA (BigQuery) : <b>{len(all_titles)}</b></div>", unsafe_allow_html=True)
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
