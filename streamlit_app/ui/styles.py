import streamlit as st

def apply_custom_styles():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;900&display=swap');

        * { font-family: 'Inter', sans-serif; }

        .stApp {
            background: linear-gradient(160deg, #EBF3FF 0%, #F7FAFF 60%, #FFFFFF 100%);
        }

        .main .block-container {
            padding-top: 2.5rem;
            padding-bottom: 3rem;
            max-width: 1200px;
        }

        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #1A4B8C 0%, #1E3A6E 100%) !important;
            border-right: none;
        }

        /* Tous les textes dans la sidebar */
        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] span,
        [data-testid="stSidebar"] div {
            color: #FFFFFF !important;
        }

        /* Champs de sélection (selectbox, multiselect) */
        [data-testid="stSidebar"] [data-baseweb="select"] > div,
        [data-testid="stSidebar"] [data-baseweb="select"] input {
            background-color: rgba(255,255,255,0.15) !important;
            border-color: rgba(255,255,255,0.35) !important;
            color: #FFFFFF !important;
            border-radius: 8px !important;
        }

        /* Dropdown ouvert — s'affiche sur le fond blanc, doit avoir son propre fond */
        [data-baseweb="popover"],
        [data-baseweb="popover"] [data-baseweb="menu"],
        [data-baseweb="menu-item"],
        ul[role="listbox"] {
            background-color: #1E3A6E !important;
            border: 1px solid rgba(255,255,255,0.15) !important;
            border-radius: 10px !important;
        }
        [data-baseweb="popover"] li,
        [data-baseweb="menu-item"],
        ul[role="listbox"] li,
        [data-baseweb="option"] {
            background-color: #1E3A6E !important;
            color: #FFFFFF !important;
        }
        [data-baseweb="popover"] li:hover,
        [data-baseweb="option"]:hover,
        [data-baseweb="menu-item"]:hover {
            background-color: rgba(255,255,255,0.12) !important;
            color: #FFFFFF !important;
        }

        /* Tags multiselect sélectionnés */
        [data-testid="stSidebar"] [data-baseweb="tag"] {
            background-color: rgba(255,255,255,0.25) !important;
            color: #FFFFFF !important;
        }

        /* Slider — track et thumb */
        [data-testid="stSidebar"] [data-testid="stSlider"] [role="slider"] {
            background-color: #FFFFFF !important;
        }
        [data-testid="stSidebar"] .stSlider [data-baseweb="slider"] div[aria-valuemin] {
            background: rgba(255,255,255,0.3) !important;
        }
        [data-testid="stSidebar"] [data-testid="stSlider"] span {
            color: #FFFFFF !important;
        }

        .movie-card {
            background: #FFFFFF;
            border-radius: 20px;
            border: 1px solid rgba(26, 75, 140, 0.12);
            padding: 30px;
            box-shadow: 0 8px 32px rgba(26, 75, 140, 0.10);
            margin-top: 25px;
        }

        .movie-title-header {
            font-size: 2.5rem;
            font-weight: 900;
            background: linear-gradient(135deg, #1A4B8C, #2E7ED6);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 15px;
        }

        .badge {
            display: inline-block; padding: 5px 12px; border-radius: 8px;
            font-size: 0.8rem; font-weight: 700; margin-right: 8px; margin-bottom: 8px;
            text-transform: uppercase; letter-spacing: 0.5px;
        }
        .rating-badge { background-color: rgba(245, 158, 11, 0.12); color: #B45309; border: 1px solid rgba(245, 158, 11, 0.3); }
        .date-badge { background-color: rgba(26, 75, 140, 0.08); color: #1A4B8C; border: 1px solid rgba(26, 75, 140, 0.2); }
        .runtime-badge { background-color: rgba(26, 75, 140, 0.08); color: #1A4B8C; border: 1px solid rgba(26, 75, 140, 0.2); }
        .genre-badge { background-color: rgba(46, 126, 214, 0.1); color: #1A4B8C; border: 1px solid rgba(46, 126, 214, 0.25); }

        .synopsis-text { color: #475569; line-height: 1.8; font-size: 1.05rem; }
        .custom-divider {
            height: 1px;
            background: linear-gradient(to right, rgba(26,75,140,0.2), transparent);
            margin: 25px 0;
        }

        .grid-card {
            background: #FFFFFF;
            border-radius: 14px;
            border: 1px solid rgba(26, 75, 140, 0.10);
            padding: 16px 20px;
            transition: all 0.25s ease;
            box-shadow: 0 2px 8px rgba(26, 75, 140, 0.06);
        }

        .grid-card:hover {
            border-color: rgba(26, 75, 140, 0.35);
            box-shadow: 0 6px 20px rgba(26, 75, 140, 0.14);
            transform: translateY(-2px);
        }

        .grid-card-title {
            font-size: 1rem;
            font-weight: 700;
            color: #1E293B;
            margin-bottom: 6px;
            line-height: 1.3;
        }

        /* Streamlit button overrides */
        .stButton > button {
            background: linear-gradient(135deg, #1A4B8C, #2E7ED6) !important;
            color: #FFFFFF !important;
            border: none !important;
            border-radius: 10px !important;
            font-weight: 600 !important;
            transition: all 0.25s ease !important;
        }
        .stButton > button:hover {
            transform: translateY(-1px) !important;
            box-shadow: 0 6px 20px rgba(26, 75, 140, 0.35) !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
