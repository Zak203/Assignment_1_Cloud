import streamlit as st

def apply_custom_styles():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Netflix+Sans:wght@300;400;500;700&family=Inter:wght@400;600;700;900&display=swap');

        /* Netflix Color Palette */
        :root {
            --netflix-red: #E50914;
            --netflix-black: #141414;
            --netflix-dark: #1F1F1F;
            --netflix-gray: #808080;
            --netflix-light: #E5E5E5;
        }

        * { font-family: 'Inter', sans-serif; }

        /* Dark Mode Global Background */
        .stApp {
            background-color: var(--netflix-black) !important;
            color: var(--netflix-light) !important;
        }

        /* Hide Top Right Menu and Footer */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {background-color: transparent !important;}

        .main .block-container {
            padding-top: 1rem;
            padding-bottom: 3rem;
            max-width: 1400px;
        }

        /* Sidebar Styling Netflix Style */
        [data-testid="stSidebar"] {
            background-color: var(--netflix-black) !important;
            border-right: 1px solid #333 !important;
        }
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p, 
        [data-testid="stSidebar"] label {
            color: #FFFFFF !important;
            font-weight: 600 !important;
        }
        
        /* Inputs styling securely applied */
        input, .stSelectbox div[data-baseweb="select"] > div, .stMultiSelect div[data-baseweb="select"] > div {
            background-color: #2b2b2b !important;
            color: white !important;
            border: 1px solid #444 !important;
            border-radius: 4px !important;
        }
        
        [data-baseweb="popover"], [data-baseweb="menu"], ul[role="listbox"] {
            background-color: #2b2b2b !important;
            border: 1px solid #444 !important;
            color: white !important;
        }
        [data-baseweb="menu-item"], [data-baseweb="option"] {
            background-color: transparent !important;
            color: white !important;
        }
        [data-baseweb="menu-item"]:hover, [data-baseweb="option"]:hover {
            background-color: var(--netflix-red) !important;
        }

        /* ----- Buttons (Netflix Red) ----- */
        .stButton > button {
            background-color: var(--netflix-red) !important;
            color: #FFFFFF !important;
            border: none !important;
            border-radius: 4px !important;
            font-weight: 700 !important;
            padding: 0.5rem 1rem !important;
            transition: all 0.2s ease !important;
        }
        .stButton > button:hover {
            background-color: #f40612 !important;
            transform: scale(1.02) !important;
        }

        button[kind="secondary"] {
            background-color: rgba(109, 109, 110, 0.7) !important;
            color: white !important;
        }
        button[kind="secondary"]:hover {
            background-color: rgba(109, 109, 110, 0.9) !important;
        }

        /* ----- Classic Catalog Row (Badges) ----- */
        .grid-card-dark {
            background: #222222;
            border-radius: 8px;
            border: 1px solid #333;
            padding: 12px 18px;
            margin-bottom: 6px;
            transition: border-color 0.2s;
        }
        .grid-card-dark:hover {
            border-color: var(--netflix-red);
        }
        .grid-card-title {
            font-size: 1rem;
            font-weight: 700;
            color: #FFF;
            margin-bottom: 0;
        }
        .badge {
            display: inline-block; padding: 2px 8px; border-radius: 6px;
            font-size: 0.7rem; font-weight: 700; text-transform: uppercase;
        }
        .rating-badge { background-color: rgba(245, 158, 11, 0.2); color: #F59E0B; border: 1px solid rgba(245, 158, 11, 0.4); }
        .lang-badge { background-color: rgba(255, 255, 255, 0.1); color: #CCC; border: 1px solid #555; }
        .genre-badge { background-color: rgba(229, 9, 20, 0.15); color: #ff545d; border: 1px solid rgba(229, 9, 20, 0.4); }

        /* ----- Movie Cards (Grid) ----- */
        .movie-card-container {
            position: relative;
            border-radius: 6px;
            overflow: hidden;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            background-color: var(--netflix-dark);
            cursor: pointer;
            margin-bottom: 1rem;
        }
        .movie-card-container:hover {
            transform: scale(1.05);
            box-shadow: 0 10px 20px rgba(0,0,0,0.8);
            z-index: 10;
        }
        .movie-info { padding: 10px; }
        .movie-title {
            font-size: 0.9rem;
            font-weight: 700;
            color: white;
            margin-bottom: 2px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        .movie-meta {
            font-size: 0.75rem;
            color: var(--netflix-gray);
            margin-bottom: 8px;
        }

        /* ----- Custom Headers ----- */
        h1, h2, h3, h4, h5 {
            color: white !important;
            font-weight: 700 !important;
        }

        .row-title {
            font-size: 1.4rem;
            font-weight: 700;
            margin-top: 2rem;
            margin-bottom: 1rem;
            color: #E5E5E5;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
