import streamlit as st
import requests
import os
import re
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
        resp = requests.post(
            f"{ML_BACKEND_URL}/recommend",
            json={"movie_ids": list(movie_ids), "top_n": top_n, "posters": False},
            timeout=30
        )
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
            match = re.search(r'\((\d{4})\)', m.get('title', ''))
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
    """Render a 5-column gallery layout for all views."""
    if not items: return

    st.markdown(f"<div class='row-title'>{title}</div>", unsafe_allow_html=True)
    display_items = items[:20] if not is_objects else items

    for m in display_items:
        tmdb_id = m.tmdb_id if is_objects else (
            m.get("tmdbId") or
            (movies_dict.get(m.get("title", ""), {}) if movies_dict else {}).get("tmdbId")
        )
        poster_url = None if is_objects else m.get("poster_url")
        if not poster_url and tmdb_id:
            if is_objects:
                m.poster_url = get_poster_url(tmdb_id)
            else:
                m["poster_url"] = get_poster_url(tmdb_id)

    lang_map = {'en': 'EN', 'fr': 'FR', 'ja': 'JA', 'es': 'ES', 'ko': 'KO', 'de': 'DE', 'it': 'IT', 'pt': 'PT', 'zh': 'ZH'}

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
                genres_raw = getattr(item, 'genres', '') or ''
                lang = getattr(item, 'language', '') or ''
            else:
                title_str = item.get("title", "")
                info = movies_dict.get(title_str, {}) if movies_dict else {}
                rating = round(item.get("avg_rating", 0), 1) if item.get("avg_rating") else 0
                tmdb_id = item.get("tmdbId") or info.get("tmdbId")
                m_ml_id = item.get("movieId") or info.get("movieId")
                ml_score = round(float(item.get("score")), 2) if item.get("score") else None
                poster_url = item.get("poster_url")
                genres_raw = item.get('genres', '') or info.get('genres', '') or ''
                lang = info.get('language', '') or item.get('language', '') or ''

            year_match = re.search(r'\((\d{4})\)', title_str)
            year = year_match.group(1) if year_match else ''
            clean_title = re.sub(r'\s*\(\d{4}\)\s*$', '', title_str).strip()

            genres_list = [g.strip() for g in genres_raw.split('|') if g.strip()][:2]
            genre_pills = ''.join([
                f"<span style='background:rgba(229,9,20,0.18);color:#e07070;"
                f"border-radius:3px;padding:1px 6px;font-size:0.6rem;"
                f"margin-right:3px;letter-spacing:0.02em;'>{g}</span>"
                for g in genres_list
            ])

            lang_label = lang_map.get(lang, lang.upper() if lang else '')
            lang_pill = (
                f"<span style='background:rgba(255,255,255,0.07);color:#888;"
                f"border-radius:3px;padding:1px 5px;font-size:0.6rem;'>{lang_label}</span>"
                if lang_label else ''
            )

            score_color = '#46d369' if ml_score else '#e0b050'
            score_val = (
                f"🎯 Score IA : {ml_score}" if ml_score
                else (f"⭐ {rating} / 5" if rating else "")
            )

            st.markdown("<div class='movie-card-container'>", unsafe_allow_html=True)
            if poster_url:
                st.markdown(
                    f"<img src='{poster_url}' style='width:100%; aspect-ratio:2/3; "
                    f"object-fit:cover; border-radius:6px; box-shadow:0 4px 12px rgba(0,0,0,0.6);'>",
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    "<div style='width:100%; aspect-ratio:2/3; background:#181818; border-radius:6px; "
                    "display:flex; align-items:center; justify-content:center;'>"
                    "<span style='color:#444; font-size:0.72rem;'>Pas d'image</span></div>",
                    unsafe_allow_html=True
                )

            st.markdown(f"""
<div class='movie-info'>
  <div class='movie-title'>{clean_title}</div>
  <div style='display:flex;align-items:center;gap:5px;margin:3px 0;flex-wrap:wrap;'>
    {f"<span style='color:#666;font-size:0.68rem;'>{year}</span>" if year else ''}
    {lang_pill}
  </div>
  <div style='margin:3px 0 4px 0;'>{genre_pills}</div>
  {f"<div class='movie-meta' style='color:{score_color};font-weight:600;'>{score_val}</div>" if score_val else ''}
</div>
""", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

            c1, c2 = st.columns([1, 1])
            with c1:
                if m_ml_id:
                    is_liked = m_ml_id in st.session_state.get("liked_movies", set())
                    lbl = "❌" if is_liked else "🤍"
                    fake_dict = {"movieId": m_ml_id, "title": title_str, "tmdbId": tmdb_id, "poster_url": poster_url}
                    st.button(lbl, key=f"gal_like_{salt}_{idx}_{m_ml_id}", on_click=toggle_like, args=(fake_dict,), use_container_width=True)
            with c2:
                if tmdb_id:
                    st.button("📖", key=f"gal_det_{salt}_{idx}_{tmdb_id}", on_click=view_details, args=(tmdb_id,), use_container_width=True)
            st.write("")


def show_netflix_home():
    # ── Handle banner card click via query param ──
    try:
        movie_param = st.query_params.get("movie_id")
        if movie_param:
            st.session_state.view_movie_id = movie_param
            st.query_params.clear()
            st.rerun()
    except Exception:
        pass

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
/* ── Page background design ── */
.stApp {
    background: radial-gradient(ellipse at top, #1a0a0a 0%, #0d0d0d 40%, #080808 100%) !important;
}
.stApp::before {
    content: '';
    position: fixed;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent 0%, #E50914 25%, #ff2d3a 50%, #E50914 75%, transparent 100%);
    z-index: 9999;
}

.block-container { padding-top: 1.2rem !important; padding-bottom: 2rem !important; }

/* ── Netflix UNIL Title ── */
.nf-title-wrap {
    display: flex;
    align-items: baseline;
    gap: 0;
    padding: 6px 0 10px 0;
    line-height: 1;
}
.nf-title-netflix {
    font-size: 2.8rem;
    font-weight: 900;
    letter-spacing: -1.5px;
    font-family: 'Inter', sans-serif;
    background: linear-gradient(145deg, #ff1a24 0%, #E50914 40%, #c20810 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    text-transform: uppercase;
    filter: drop-shadow(0 2px 12px rgba(229,9,20,0.35));
}
.nf-title-unil {
    font-size: 2.8rem;
    font-weight: 200;
    letter-spacing: 10px;
    color: rgba(255,255,255,0.85);
    margin-left: 10px;
    text-transform: uppercase;
    font-family: 'Inter', sans-serif;
}

/* ── Navigation : texte souligné rouge, pas de bouton ── */
#nav-row .stButton > button {
    background: transparent !important;
    border: none !important;
    border-bottom: 2px solid transparent !important;
    border-radius: 0 !important;
    color: #777 !important;
    font-size: 0.78rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    padding: 2px 0 6px 0 !important;
    box-shadow: none !important;
    min-height: 0 !important;
    height: auto !important;
    width: auto !important;
    transition: color 0.18s ease !important;
}
#nav-row .stButton > button:hover {
    color: #fff !important;
    background: transparent !important;
    box-shadow: none !important;
    transform: none !important;
}
#nav-row .stButton > button[kind="primary"] {
    color: #fff !important;
    border-bottom: 2px solid #E50914 !important;
    font-weight: 700 !important;
}

/* ── Filtres : épurés, uniformes, sans contour ── */
/* Supprime toute boîte autour des select/multiselect */
div[data-baseweb="select"] > div,
div[data-baseweb="select"] > div > div {
    background-color: transparent !important;
    border: none !important;
    border-bottom: 1px solid #2a2a2a !important;
    border-radius: 0 !important;
    color: #bbb !important;
    font-size: 0.8rem !important;
    min-height: 32px !important;
    padding: 0 2px !important;
    box-shadow: none !important;
}
div[data-baseweb="select"]:hover > div {
    border-bottom: 1px solid #555 !important;
}
div[data-baseweb="select"]:focus-within > div {
    border-bottom: 1px solid #E50914 !important;
}
/* Texte sélectionné */
div[data-baseweb="select"] [class*="singleValue"],
div[data-baseweb="select"] [class*="SingleValue"] {
    color: #bbb !important;
    font-size: 0.8rem !important;
}
/* Placeholder */
div[data-baseweb="select"] [class*="placeholder"],
div[data-baseweb="select"] input::placeholder {
    color: #555 !important;
    font-size: 0.8rem !important;
}
/* Flèche dropdown */
div[data-baseweb="select"] svg {
    color: #444 !important;
    width: 14px !important;
    height: 14px !important;
}
/* Tags multiselect */
span[data-baseweb="tag"] {
    background-color: rgba(229,9,20,0.18) !important;
    border: none !important;
    color: #e07070 !important;
    border-radius: 3px !important;
    font-size: 0.72rem !important;
    padding: 1px 6px !important;
}
span[data-baseweb="tag"] svg { color: #e07070 !important; }
/* Menu dropdown */
[data-baseweb="popover"],
[data-baseweb="menu"],
ul[role="listbox"] {
    background-color: #141414 !important;
    border: 1px solid #2a2a2a !important;
    border-radius: 4px !important;
    box-shadow: 0 8px 32px rgba(0,0,0,0.8) !important;
}
[data-baseweb="option"] {
    color: #bbb !important;
    font-size: 0.8rem !important;
    background: transparent !important;
    padding: 6px 12px !important;
}
[data-baseweb="option"]:hover,
[data-baseweb="option"][aria-selected="true"] {
    background-color: rgba(229,9,20,0.18) !important;
    color: #fff !important;
}

/* ── Séparateur ── */
hr.nf-sep {
    border: none;
    border-top: 1px solid #1e1e1e;
    margin: 8px 0 14px 0;
}

/* ── Gallery cards ── */
.movie-card-container { margin-bottom: 6px; }
.movie-info { padding: 6px 2px 2px 2px; }
.movie-title {
    font-size: 0.8rem;
    font-weight: 700;
    color: #e5e5e5;
    line-height: 1.25;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
}
.movie-meta {
    font-size: 0.7rem;
    color: #888;
    margin-top: 3px;
}

/* Boutons like / détail des cards : petits et discrets */
.stButton > button[data-testid*="gal_like_"],
.stButton > button[data-testid*="gal_det_"] {
    background: rgba(255,255,255,0.06) !important;
    border: none !important;
    color: #999 !important;
    font-size: 0.78rem !important;
    padding: 2px 6px !important;
    min-height: 0 !important;
    height: 26px !important;
    border-radius: 3px !important;
    box-shadow: none !important;
}
.stButton > button[data-testid*="gal_like_"]:hover,
.stButton > button[data-testid*="gal_det_"]:hover {
    background: rgba(229,9,20,0.25) !important;
    color: #fff !important;
    transform: none !important;
}

/* ── Row title ── */
.row-title {
    font-size: 1.05rem;
    font-weight: 700;
    color: #d0d0d0;
    margin: 22px 0 12px 0;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    display: flex;
    align-items: center;
    gap: 8px;
}
.row-title::before {
    content: '';
    display: inline-block;
    width: 3px;
    height: 16px;
    background: #E50914;
    border-radius: 2px;
    flex-shrink: 0;
}

/* ── Trending Banner ── */
@keyframes scrollBanner {
    0%   { transform: translateX(0); }
    100% { transform: translateX(-50%); }
}
.banner-wrapper {
    overflow: hidden;
    padding: 10px 0 16px 0;
    position: relative;
}
.banner-wrapper::before,
.banner-wrapper::after {
    content: '';
    position: absolute;
    top: 0; bottom: 0;
    width: 80px;
    z-index: 2;
    pointer-events: none;
}
.banner-wrapper::before {
    left: 0;
    background: linear-gradient(90deg, #0d0d0d 0%, transparent 100%);
}
.banner-wrapper::after {
    right: 0;
    background: linear-gradient(-90deg, #0d0d0d 0%, transparent 100%);
}
.banner-track {
    display: flex;
    gap: 10px;
    animation: scrollBanner 110s linear infinite;
    width: max-content;
}
/* Pause au survol */
.banner-wrapper:hover .banner-track {
    animation-play-state: paused !important;
}
.banner-card {
    flex-shrink: 0;
    width: 155px;
    border-radius: 6px;
    overflow: hidden;
    box-shadow: 0 4px 18px rgba(0,0,0,0.65);
    position: relative;
    transition: transform 0.22s ease, box-shadow 0.22s ease;
    cursor: pointer;
    text-decoration: none;
    display: block;
}
.banner-card:hover {
    transform: scale(1.07) translateY(-3px);
    box-shadow: 0 10px 32px rgba(229,9,20,0.35);
    z-index: 5;
}
.banner-card img {
    width: 155px;
    height: 232px;
    object-fit: cover;
    display: block;
}
.banner-card .overlay {
    position: absolute;
    bottom: 0; left: 0; right: 0;
    padding: 8px 7px 7px 7px;
    background: linear-gradient(transparent 0%, rgba(0,0,0,0.75) 40%, rgba(0,0,0,0.95) 100%);
}
.banner-card .b-title {
    font-size: 0.7rem;
    font-weight: 700;
    color: #fff;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    margin-bottom: 2px;
}
.banner-card .b-year {
    font-size: 0.6rem;
    color: #999;
    margin-bottom: 1px;
}
.banner-card .b-genres {
    font-size: 0.58rem;
    color: #777;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    margin-bottom: 2px;
}
.banner-card .b-score {
    font-size: 0.62rem;
    color: #46d369;
    font-weight: 700;
}
/* Overlay rouge au hover pour indiquer le clic */
.banner-card::after {
    content: '▶ Voir';
    position: absolute;
    top: 50%; left: 50%;
    transform: translate(-50%, -50%);
    background: rgba(229,9,20,0.85);
    color: #fff;
    font-size: 0.7rem;
    font-weight: 700;
    padding: 5px 10px;
    border-radius: 4px;
    opacity: 0;
    transition: opacity 0.18s ease;
    letter-spacing: 0.05em;
    pointer-events: none;
    white-space: nowrap;
}
.banner-card:hover::after { opacity: 1; }

/* ── Section label ── */
.section-label {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 8px;
}
.section-label-bar {
    width: 3px; height: 16px;
    background: #E50914;
    border-radius: 2px;
}
.section-label-text {
    font-size: 0.9rem;
    font-weight: 700;
    color: #d0d0d0;
    letter-spacing: 0.06em;
    text-transform: uppercase;
}
.section-label-hint {
    font-size: 0.68rem;
    color: #444;
    margin-left: 2px;
}
</style>
""", unsafe_allow_html=True)

    # ── ROW 1 : Title + Filters ──
    col_t, col_lang, col_genre, col_rat, col_yr = st.columns([3.2, 1.2, 1.6, 1.1, 1.1])
    with col_t:
        st.markdown(
            "<div class='nf-title-wrap'>"
            "<span class='nf-title-netflix'>Netflix</span>"
            "<span class='nf-title-unil'>UNIL</span>"
            "</div>",
            unsafe_allow_html=True
        )
    with col_lang:
        lang_options = {
            "Langue": None, "Anglais": "en", "Français": "fr",
            "Espagnol": "es", "Japonais": "ja", "Coréen": "ko"
        }
        language_label = st.selectbox("Langue", list(lang_options.keys()), label_visibility="collapsed")
    with col_genre:
        genres_list = fetch_genres()
        genre = st.multiselect("Genre(s)", genres_list, placeholder="Genre", label_visibility="collapsed")
    with col_rat:
        min_avg_rating = st.selectbox(
            "Note", [0.0, 1.0, 2.0, 3.0, 4.0, 4.5],
            format_func=lambda x: f"≥ {x} ⭐" if x > 0 else "Note ⭐",
            label_visibility="collapsed"
        )
    with col_yr:
        released_after_year = st.selectbox(
            "Année", [1900, 1980, 1990, 2000, 2010, 2020],
            format_func=lambda x: f"≥ {x}" if x > 1900 else "Année",
            label_visibility="collapsed"
        )

    # ── ROW 2 : Search + Nav ──
    if "current_tab" not in st.session_state:
        st.session_state.current_tab = "Accueil"

    def set_tab(t):
        st.session_state.current_tab = t

    all_titles = sorted(list(movies_dict.keys()))
    if "search_widget" not in st.session_state:
        st.session_state.search_widget = ""

    def on_search_selected():
        info = movies_dict.get(st.session_state.search_widget)
        if info and info.get("tmdbId"):
            st.session_state.search_widget = ""
            view_details(info["tmdbId"])

    n_favs = len(st.session_state.get('liked_movies', set()))

    st.markdown("<div id='nav-row'>", unsafe_allow_html=True)
    c_s, c1, c2, c3, c4 = st.columns([1.5, 1, 2, 2, 1.8])
    with c_s:
        st.selectbox(
            "🔍", ["🔍 Rechercher..."] + all_titles,
            key="search_widget", on_change=on_search_selected,
            label_visibility="collapsed"
        )
    with c1:
        st.button("Accueil", key="nav_home", on_click=set_tab, args=("Accueil",),
                  type="primary" if st.session_state.current_tab == "Accueil" else "secondary")
    with c2:
        st.button("Recommandations", key="nav_rec", on_click=set_tab, args=("Recommandations",),
                  type="primary" if st.session_state.current_tab == "Recommandations" else "secondary")
    with c3:
        st.button("Catalogue Complet", key="nav_cat", on_click=set_tab, args=("Catalogue Complet",),
                  type="primary" if st.session_state.current_tab == "Catalogue Complet" else "secondary")
    with c4:
        st.button(f"Favoris ({n_favs})", key="nav_fav", on_click=set_tab, args=("Mes Favoris",),
                  type="primary" if st.session_state.current_tab == "Mes Favoris" else "secondary")
    st.markdown("</div>", unsafe_allow_html=True)

    current_tab = st.session_state.current_tab
    target_language = lang_options[language_label]
    page_size = 20

    st.markdown("<hr class='nf-sep'>", unsafe_allow_html=True)

    # ── CONTENT ──
    if current_tab == "Accueil":
        with st.spinner("Chargement des tendances..."):
            popular_movies = fetch_popular_movies(top_n=40)
            popular_movies = apply_ml_filters(
                popular_movies, genre, float(min_avg_rating),
                int(released_after_year), target_language, movies_dict
            )

            banner_cards = ""
            for m in popular_movies[:40]:
                tmdb_id = m.get("tmdbId")
                if not m.get("poster_url") and tmdb_id:
                    m["poster_url"] = get_poster_url(tmdb_id)
                if m.get("poster_url"):
                    t = m.get('title', '')
                    clean_t = re.sub(r'\s*\(\d{4}\)\s*$', '', t).strip()
                    ym = re.search(r'\((\d{4})\)', t)
                    year = ym.group(1) if ym else ''
                    genres_raw = m.get('genres', '') or ''
                    genres_disp = ' · '.join([g.strip() for g in genres_raw.split('|') if g.strip()][:2])
                    sc = m.get('avg_rating', 0)
                    sc_txt = f"<div class='b-score'>⭐ {round(sc,1)}</div>" if sc else ""
                    year_txt = f"<div class='b-year'>{year}</div>" if year else ""
                    gen_txt = f"<div class='b-genres'>{genres_disp}</div>" if genres_disp else ""
                    link = f"?movie_id={tmdb_id}" if tmdb_id else "#"
                    banner_cards += (
                        f"<a href='{link}' target='_self' style='text-decoration:none;'>"
                        f"<div class='banner-card'>"
                        f"<img src='{m['poster_url']}' loading='lazy'>"
                        f"<div class='overlay'>"
                        f"<div class='b-title'>{clean_t}</div>"
                        f"{year_txt}{gen_txt}{sc_txt}"
                        f"</div></div></a>"
                    )

            if banner_cards:
                st.markdown(
                    "<div class='section-label'>"
                    "<div class='section-label-bar'></div>"
                    "<span class='section-label-text'>Tendances Actuelles</span>"
                    "<span class='section-label-hint'>— hover pour pause · clic pour ouvrir</span>"
                    "</div>",
                    unsafe_allow_html=True
                )
                st.markdown(
                    f"<div class='banner-wrapper'>"
                    f"<div class='banner-track'>{banner_cards}{banner_cards}</div>"
                    f"</div>",
                    unsafe_allow_html=True
                )

        if len(st.session_state.liked_movies) > 0:
            with st.spinner("L'IA analyse vos goûts..."):
                recommendations = fetch_recommendations(st.session_state.liked_movies, top_n=20)
                recommendations = apply_ml_filters(
                    recommendations, genre, float(min_avg_rating),
                    int(released_after_year), target_language, movies_dict
                )
            if recommendations:
                render_unified_movie_gallery(
                    "✨ Recommandé pour vous", recommendations,
                    salt="rec_preview", movies_dict=movies_dict
                )

    elif current_tab == "Recommandations":
        if len(st.session_state.liked_movies) > 0:
            with st.spinner("L'IA calcule vos recommandations personnalisées..."):
                recommendations = fetch_recommendations(st.session_state.liked_movies, top_n=100)
                recommendations = apply_ml_filters(
                    recommendations, genre, float(min_avg_rating),
                    int(released_after_year), target_language, movies_dict
                )
            if recommendations:
                render_unified_movie_gallery(
                    "🎯 Vos Coups de Cœur", recommendations,
                    salt="rec_full", movies_dict=movies_dict
                )
            else:
                st.info("Aucune recommandation ne correspond à vos filtres.")
        else:
            st.info("💡 Likez quelques films pour activer l'IA ! En attendant, voici les tendances :")
            with st.spinner("Chargement..."):
                popular_movies = fetch_popular_movies(top_n=30)
                popular_movies = apply_ml_filters(
                    popular_movies, genre, float(min_avg_rating),
                    int(released_after_year), target_language, movies_dict
                )
                render_unified_movie_gallery(
                    "🔥 Sélection Découverte", popular_movies,
                    salt="cold", movies_dict=movies_dict
                )

    elif current_tab == "Mes Favoris":
        if len(st.session_state.liked_movies) > 0:
            liked_list = list(st.session_state.liked_movies_data.values())
            liked_list = apply_ml_filters(
                liked_list, genre, float(min_avg_rating),
                int(released_after_year), target_language, movies_dict
            )
            if liked_list:
                render_unified_movie_gallery(
                    "🤍 Mes Favoris", liked_list[::-1],
                    salt="fav", movies_dict=movies_dict
                )
            else:
                st.info("Aucun favori ne correspond à ces filtres.")
        else:
            st.info("Votre liste de favoris est vide.")

    elif current_tab == "Catalogue Complet":
        payload = {"page": st.session_state.page, "page_size": page_size}
        if lang_options[language_label]:
            payload["language"] = lang_options[language_label]
        if genre:
            payload["genre"] = "|".join(genre)
        if float(min_avg_rating) > 0:
            payload["min_avg_rating"] = float(min_avg_rating)
        if int(released_after_year) > 1900:
            payload["released_after"] = int(released_after_year)

        with st.spinner("Chargement du catalogue..."):
            catalog_movies = fetch_filtered_movies(payload)

        if catalog_movies:
            render_unified_movie_gallery(
                "🎬 Catalogue complet", catalog_movies,
                is_objects=True, salt="cat", movies_dict=movies_dict
            )
            col_prev, col_center, col_next = st.columns([1, 2, 1])
            with col_prev:
                if st.session_state.page > 1:
                    if st.button("⬅️ Retour", key="btn_prev"):
                        st.session_state.page -= 1
                        st.rerun()
            with col_center:
                st.markdown(
                    f'<p style="text-align:center;color:#444;margin-top:8px;font-size:0.78rem;">'
                    f'Page {st.session_state.page}</p>',
                    unsafe_allow_html=True
                )
            with col_next:
                if len(catalog_movies) == page_size:
                    if st.button("Suivant ➡️", key="btn_next"):
                        st.session_state.page += 1
                        st.rerun()
        else:
            st.info("Aucun film ne correspond à vos filtres.")
