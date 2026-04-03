import streamlit as st
import re
from api.services import fetch_tmdb_movie_details
from api.elasticsearch_service import fetch_all_movies_dict
from ui.styles import apply_custom_styles
from ui.interactions import toggle_like

def _find_movie_id(movies_dict, tmdb_title, movie_id):
    """Cherche le movieId en base : d'abord par tmdbId (fiable), puis par titre."""
    # 1) Scan par tmdbId — le plus fiable
    for details in movies_dict.values():
        if str(details.get("tmdbId")) == str(movie_id):
            return details.get("movieId")
    # 2) Fallback : titre exact TMDB
    info = movies_dict.get(tmdb_title)
    if info:
        return info.get("movieId")
    # 3) Fallback : titre normalisé (gère "The Matrix" ↔ "Matrix, The (1999)")
    title_clean = re.sub(r'\s*\(\d{4}\)\s*$', '', tmdb_title).strip().lower()
    for key, details in movies_dict.items():
        key_clean = re.sub(r'\s*\(\d{4}\)\s*$', '', key).strip().lower()
        key_clean = re.sub(r'^(.*),\s*(the|a|an)$', r'\2 \1', key_clean).strip()
        if key_clean == title_clean:
            return details.get("movieId")
    return None

def show_movie_detail_page(movie_id):
    apply_custom_styles()
    
    if st.button("⬅️ Retour au catalogue"):
        del st.session_state.view_movie_id
        st.rerun()
    
    with st.spinner("Chargement de la fiche..."):
        movie = fetch_tmdb_movie_details(movie_id)
    
    if not movie:
        st.error("Impossible de charger les détails du film.")
        return
    
    st.markdown('<div class="movie-card">', unsafe_allow_html=True)
    
    col_poster, col_info = st.columns([1, 2], gap="large")
    
    with col_poster:
        if movie.poster_url:
            st.image(movie.poster_url, width=350)
        else:
            st.info("Affiche non disponible")
    
    with col_info:
        # Title + Like button in a row
        title_col, like_col = st.columns([3, 1])
        with title_col:
            st.markdown(f'<div class="movie-title-header">{movie.title}</div>', unsafe_allow_html=True)
            
        with like_col:
            movies_dict = fetch_all_movies_dict()
            m_ml_id = _find_movie_id(movies_dict, movie.title, movie_id) if movies_dict else None

            if m_ml_id:
                is_liked = m_ml_id in st.session_state.get("liked_movies", set())
                like_label = "❌ Retirer" if is_liked else "🤍 Liker"
                fake_dict = {
                    "movieId": m_ml_id,
                    "title": movie.title,
                    "tmdbId": movie_id,
                    "poster_url": movie.poster_url
                }
                st.button(like_label, key=f"det_like_{movie_id}", on_click=toggle_like, args=(fake_dict,), use_container_width=True)
            else:
                st.caption("❓ Film non indexé")

        
        if movie.tagline:
            st.markdown(f'<p style="color: #64748B; font-style: italic; font-size: 1.1rem; margin-bottom: 20px;">"{movie.tagline}"</p>', unsafe_allow_html=True)
        
        st.markdown(f"""
            <span class="badge rating-badge">⭐ {movie.vote_average}/10 ({movie.vote_count} votes)</span>
            <span class="badge date-badge">📅 {movie.release_date}</span>
            <span class="badge runtime-badge">⏱️ {movie.runtime} min</span>
        """, unsafe_allow_html=True)
        
        if movie.genres_names:
            genres_html = "".join([f'<span class="badge genre-badge">{g}</span>' for g in movie.genres_names])
            st.markdown(f"<div style='margin-top: 10px;'>{genres_html}</div>", unsafe_allow_html=True)
        
        st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
        st.markdown('<p style="color: #1A4B8C; font-weight: 700; margin-bottom: 10px; font-size: 1.1rem;">SYNOPSIS</p>', unsafe_allow_html=True)
        st.markdown(f'<div class="synopsis-text">{movie.overview}</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.markdown('<p style="color: #64748B; font-size: 0.9rem;">BUDGET</p>', unsafe_allow_html=True)
        st.markdown(f'<p style="color: #1A4B8C; font-size: 1.3rem; font-weight: 700;">${movie.budget:,.0f}</p>' if movie.budget else '<p style="color: #94A3B8;">Non communiqué</p>', unsafe_allow_html=True)
    with col_b:
        st.markdown('<p style="color: #64748B; font-size: 0.9rem;">REVENUS</p>', unsafe_allow_html=True)
        st.markdown(f'<p style="color: #1A4B8C; font-size: 1.3rem; font-weight: 700;">${movie.revenue:,.0f}</p>' if movie.revenue else '<p style="color: #94A3B8;">Non communiqué</p>', unsafe_allow_html=True)
    with col_c:
        st.markdown('<p style="color: #64748B; font-size: 0.9rem;">LANGUE ORIGINALE</p>', unsafe_allow_html=True)
        st.markdown(f'<p style="color: #1A4B8C; font-size: 1.3rem; font-weight: 700;">{movie.display_language}</p>', unsafe_allow_html=True)
