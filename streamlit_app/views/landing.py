import streamlit as st
import os
from ui.styles import apply_custom_styles

def show_landing_page():
    apply_custom_styles()

    # Logo HEC
    logo_path = os.path.join(os.path.dirname(__file__), '..', 'heclogo.png')
    logo_exists = os.path.exists(logo_path)

    st.markdown(
        """
        <style>
        @keyframes float {
            0% { transform: translateY(0px); }
            50% { transform: translateY(-10px); }
            100% { transform: translateY(0px); }
        }
        @keyframes fadeInUp {
            from { opacity: 0; transform: translateY(24px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .landing-wrapper {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            text-align: center;
            padding: 3rem 1rem 2rem;
            animation: fadeInUp 0.7s ease forwards;
        }
        .hec-logo-img {
            animation: float 6s ease-in-out infinite;
            margin-bottom: 20px;
            max-width: 160px;
        }
        .landing-badge {
            display: inline-block;
            background: rgba(26, 75, 140, 0.10);
            border: 1px solid rgba(26, 75, 140, 0.30);
            color: #1A4B8C;
            font-size: 0.78rem;
            font-weight: 700;
            letter-spacing: 2px;
            text-transform: uppercase;
            padding: 6px 18px;
            border-radius: 50px;
            margin-bottom: 20px;
        }
        .landing-title {
            font-size: 3.6rem;
            font-weight: 900;
            background: linear-gradient(135deg, #1A4B8C 0%, #2E7ED6 60%, #56A0E0 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin: 0 0 16px 0;
            line-height: 1.1;
        }
        .landing-subtitle {
            font-size: 1.05rem;
            color: #64748B;
            margin-bottom: 12px;
            font-weight: 400;
            line-height: 1.6;
        }
        .landing-author {
            color: #94A3B8;
            font-size: 0.8rem;
            font-weight: 600;
            letter-spacing: 1.5px;
            text-transform: uppercase;
            margin-bottom: 0;
        }
        .stat-card {
            background: #FFFFFF;
            border: 1px solid rgba(26, 75, 140, 0.12);
            border-radius: 16px;
            padding: 22px 20px;
            text-align: center;
            box-shadow: 0 4px 16px rgba(26, 75, 140, 0.08);
            transition: all 0.3s ease;
        }
        .stat-card:hover {
            border-color: rgba(26, 75, 140, 0.3);
            transform: translateY(-3px);
            box-shadow: 0 8px 24px rgba(26, 75, 140, 0.14);
        }
        .stat-value {
            font-size: 1.9rem;
            font-weight: 900;
            color: #1A4B8C;
            line-height: 1;
        }
        .stat-label {
            font-size: 0.78rem;
            color: #64748B;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-top: 8px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Bloc héro : tout en HTML pur pour garantir le centrage sans scroll

    logo_html = ""
    if logo_exists:
        import base64
        with open(logo_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        logo_html = f'<img src="data:image/png;base64,{b64}" class="hec-logo-img" />'

    st.markdown(f"""
        <div class="landing-wrapper">
            {logo_html}
            <div class="landing-badge">☁️ Cloud and Advanced Analytics</div>
            <h1 class="landing-title">Assignment numero 1</h1>
            <p class="landing-subtitle">
                Explorez des milliers de films, filtrez par genre,<br>
                langue, année et note — le tout en temps réel.
            </p>
            <p class="landing-author">Zakaria Charouite</p>
        </div>
    """, unsafe_allow_html=True)

    # Stat cards
    col_stat1, col_stat2, col_stat3 = st.columns(3)
    with col_stat1:
        st.markdown("""
            <div class="stat-card">
                <div class="stat-value">10K+</div>
                <div class="stat-label">Films disponibles</div>
            </div>
        """, unsafe_allow_html=True)
    with col_stat2:
        st.markdown("""
            <div class="stat-card">
                <div class="stat-value">20+</div>
                <div class="stat-label">Genres différents</div>
            </div>
        """, unsafe_allow_html=True)
    with col_stat3:
        st.markdown("""
            <div class="stat-card">
                <div class="stat-value">☁️</div>
                <div class="stat-label">Powered by GCP</div>
            </div>
        """, unsafe_allow_html=True)

    st.write("")
    st.write("")

    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        if st.button("🚀  Entrer dans la bibliothèque", use_container_width=True):
            st.session_state.app_started = True
            st.rerun()
