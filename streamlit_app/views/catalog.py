import streamlit as st
import os
import base64
from api.services import fetch_genres, fetch_filtered_movies

def show_catalog_page():
    # Bannière cinéma
    banner_path = os.path.join(os.path.dirname(__file__), '..', 'cinema_banner.png')
    if os.path.exists(banner_path):
        with open(banner_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        st.markdown(f"""
            <div style="
                width: 100%;
                height: 270px;
                background-image: url('data:image/png;base64,{b64}');
                background-size: cover;
                background-position: center 20%;
                border-radius: 18px;
                margin-bottom: 1.5rem;
                position: relative;
                overflow: hidden;
                display: flex;
                align-items: flex-end;
            ">
                <div style="
                    position: absolute; inset: 0;
                    background: linear-gradient(to right, rgba(26,75,140,0.75) 0%, rgba(26,75,140,0.2) 60%, transparent 100%);
                    border-radius: 18px;
                "></div>
                <h1 style="
                    position: relative;
                    color: #FFFFFF;
                    font-weight: 900;
                    font-size: 2.4rem;
                    margin: 0 0 1.2rem 1.8rem;
                    text-shadow: 0 2px 12px rgba(0,0,0,0.4);
                    z-index: 1;
                ">🎬 Catalogue</h1>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown('<h1 style="color: #1A4B8C; font-weight: 900; margin-bottom: 2.5rem; font-size: 2.5rem;">Catalogue</h1>', unsafe_allow_html=True)


    
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
            movies.sort(key=lambda m: m.title.lower())
        elif tri == "Titre Z-A":
            movies.sort(key=lambda m: m.title.lower(), reverse=True)
        elif tri == "Année ↓":
            movies.sort(key=lambda m: m.release_year or 0, reverse=True)
        elif tri == "Année ↑":
            movies.sort(key=lambda m: m.release_year or 9999)
        elif tri == "Note ↓":
            movies.sort(key=lambda m: m.avg_rating, reverse=True)
        elif tri == "Note ↑":
            movies.sort(key=lambda m: m.avg_rating)
        
        for idx, movie in enumerate(movies):
            genre_badges = "".join(
                f'<span class="badge genre-badge" style="font-size: 0.7rem; padding: 2px 8px; margin-bottom: 0;">{g}</span>'
                for g in movie.genres_list
            )
            
            col_info, col_btn = st.columns([4, 1.4], gap="medium")
            with col_info:
                st.markdown(f"""
                    <div class="grid-card" style="padding: 12px 18px; margin-bottom: 6px;">
                        <div style="display: flex; align-items: center; gap: 12px; flex-wrap: wrap;">
                            <span style="font-size: 1.2rem;">🎬</span>
                            <div class="grid-card-title" style="margin-bottom: 0; font-size: 0.95rem;">{movie.title}</div>
                            <span style="color: #64748B; font-size: 0.8rem;">{movie.release_year or ''}</span>
                            <span style="color: #64748B; font-size: 0.7rem; border: 1px solid rgba(26,75,140,0.2); padding: 2px 6px; border-radius: 6px; background: rgba(26,75,140,0.07);">{movie.display_language}</span>
                            <span class="badge rating-badge" style="font-size: 0.75rem; padding: 2px 8px; margin-bottom: 0;">⭐ {round(movie.avg_rating, 1)}</span>
                            {genre_badges}
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            with col_btn:
                st.write("")
                if movie.tmdb_id:
                    if st.button("📖 Voir la fiche", key=f"btn_{movie.tmdb_id}_{idx}", use_container_width=True):
                        st.session_state.view_movie_id = movie.tmdb_id
                        st.rerun()
        
        st.write("")
        col_prev, col_center, col_next = st.columns([1, 2, 1])
        with col_prev:
            if st.session_state.page > 1:
                if st.button("⬅️ Retour"):
                    st.session_state.page -= 1
                    st.rerun()
        with col_center:
            st.markdown(f'<p style="text-align: center; color: #1A4B8C; font-size: 1rem; margin-top: 8px;">Page {st.session_state.page}</p>', unsafe_allow_html=True)
        with col_next:
            if len(movies) == page_size:
                if st.button("Suivant ➡️"):
                    st.session_state.page += 1
                    st.rerun()
    else:
        st.warning("Aucun film trouvé selon ces critères.")
