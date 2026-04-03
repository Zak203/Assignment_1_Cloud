import streamlit as st
import requests
import os
from api.elasticsearch_service import fetch_all_movies_dict

# URL of the ML Flask Backend (running locally or Cloud Run)
ML_BACKEND_URL = os.getenv("ML_BACKEND_URL", "http://127.0.0.1:5001")

def show_recommender_page():
    st.markdown('<h1 style="color: #1A4B8C; font-weight: 900; margin-bottom: 2.5rem; font-size: 2.5rem;">🤖 Recommandations Personnalisées</h1>', unsafe_allow_html=True)

    st.markdown("""
    Sélectionnez vos films préférés pour obtenir des recommandations personnalisées basées sur les utilisateurs ayant des goûts similaires.
    Si vous ne sélectionnez rien, nous vous proposerons les films les plus populaires.
    """)

    # Récupérer le dictionnaire Titre -> MovieId
    movies_dict = fetch_all_movies_dict()
    all_titles = sorted(list(movies_dict.keys()))

    # Sélection multiple
    selected_titles = st.multiselect(
        "Vos films préférés :",
        options=all_titles,
        placeholder="Tapez un titre de film et sélectionnez-le...",
        help="Plus vous choisissez de films, plus les recommandations seront précises."
    )

    if st.button("Voir mes recommandations", type="primary"):
        with st.spinner("Génération des recommandations en cours..."):
            
            # Map selected titles to movieIds (movies_dict values are now dicts)
            movie_ids = [movies_dict[title]["movieId"] for title in selected_titles if title in movies_dict]
            
            try:
                # Appel API au backend Flask
                response = requests.post(
                    f"{ML_BACKEND_URL}/recommend",
                    json={"movie_ids": movie_ids, "top_n": 10},
                    timeout=30
                )
                response.raise_for_status()
                data = response.json()
                results = data.get("results", [])
                
                if data.get("type") == "popular" or data.get("type") == "popular_fallback":
                    st.info("💡 Voici les films les plus populaires (aucune correspondance exacte trouvée ou aucune sélection).")
                else:
                    similar_users = data.get('similar_users', [])
                    st.success(f"✨ Recommandations générées à partir de {len(similar_users)} utilisateurs ayant des goûts similaires !")

                # Affichage des résultats avec posters
                if results:
                    st.markdown("### 🎬 Top 10 Recommandations")
                    
                    # Grille de films (5 colonnes)
                    cols = st.columns(5)
                    for i, movie in enumerate(results):
                        with cols[i % 5]:
                            poster_url = movie.get('poster_url')
                            if poster_url:
                                st.image(poster_url, use_container_width=True)
                            else:
                                st.markdown("""
                                <div style="width:100%; aspect-ratio:2/3; background:#e2e8f0; display:flex; align-items:center; justify-content:center; border-radius:8px; margin-bottom:1rem;">
                                    <span style="color:#64748B;">Pas d'image</span>
                                </div>
                                """, unsafe_allow_html=True)
                            
                            st.markdown(f"**{movie['title']}**")
                            if movie.get('release_year'):
                                st.caption(f"{movie['release_year']}")
                            if movie.get('score'):
                                st.caption(f"Score ML: {movie['score']:.2f}")
                            elif movie.get('avg_rating'):
                                st.caption(f"⭐ {movie['avg_rating']:.1f}")

                else:
                    st.warning("Aucune recommandation trouvée.")

            except requests.RequestException as e:
                st.error(f"Erreur de communication avec le moteur de recommandation : {e}")


