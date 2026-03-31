import streamlit as st
import time

def show_landing_page():
    st.markdown("""
        <style>
        /* Hide all default streamlit components including header and footer */
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        footer {visibility: hidden;}
        .block-container {
            padding-top: 0rem;
            padding-bottom: 0rem;
            padding-left: 0rem;
            padding-right: 0rem;
            max-width: 100% !important;
            height: 100vh;
        }
        
        body, .stApp {
            background-color: #000 !important;
            overflow: hidden !important;
        }

        @keyframes infiniteScroll {
            0% { transform: translateX(0); }
            100% { transform: translateX(-50%); }
        }

        @keyframes fadeInOutText {
            0% { opacity: 0; transform: scale(0.9) translateY(20px); }
            20% { opacity: 1; transform: scale(1) translateY(0); }
            80% { opacity: 1; transform: scale(1) translateY(0); }
            100% { opacity: 0; transform: scale(1.05) translateY(-20px); }
        }

        @keyframes fadeOutScreen {
            0% { opacity: 1; }
            90% { opacity: 1; }
            100% { opacity: 0; }
        }

        .splash-container {
            position: fixed;
            top: 0; left: 0; width: 100vw; height: 100vh;
            background-color: #000;
            overflow: hidden;
            z-index: 9999;
            animation: fadeOutScreen 4.5s ease-in-out forwards;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .marquee-wrapper {
            position: absolute;
            top: -10vh; left: 0; width: 200vw;
            display: flex;
            flex-direction: column;
            gap: 2vh;
            opacity: 0.25; /* Very subtle posters in the background */
            transform: rotate(-5deg) scale(1.2);
            pointer-events: none;
        }

        .marquee-row {
            display: flex;
            width: fit-content;
            animation: infiniteScroll 30s linear infinite;
        }

        .marquee-row.reverse {
            animation-direction: reverse;
            animation-duration: 40s;
        }

        .marquee-img {
            height: 35vh;
            border-radius: 12px;
            margin-right: 2vh;
            object-fit: cover;
            box-shadow: 0 4px 20px rgba(0,0,0,0.8);
        }
        
        .dark-overlay {
            position: absolute;
            top: 0; left: 0; width: 100%; height: 100%;
            background: radial-gradient(circle at center, transparent 0%, #000 80%);
            z-index: 2;
        }

        .splash-text-box {
            position: relative;
            z-index: 10;
            text-align: center;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            animation: fadeInOutText 4.5s cubic-bezier(0.16, 1, 0.3, 1) forwards;
        }

        .h1-title {
            font-size: 5rem !important;
            font-weight: 900 !important;
            color: #E50914 !important;
            letter-spacing: 0px !important;
            margin: 0 !important;
            padding: 0 !important;
            line-height: 1 !important;
            text-shadow: 0 4px 30px rgba(229, 9, 20, 0.5);
            text-transform: uppercase;
        }

        .h2-subtitle {
            font-size: 1.8rem !important;
            color: #FFF !important;
            font-weight: 300 !important;
            letter-spacing: 12px !important;
            margin-top: 1rem !important;
            margin-bottom: 2rem !important;
            text-transform: uppercase;
        }

        .h3-author {
            font-size: 1rem !important;
            color: #888 !important;
            font-weight: 400 !important;
            letter-spacing: 4px !important;
            text-transform: uppercase;
        }
        </style>
    """, unsafe_allow_html=True)

    # 12 high quality dummy Netflix posters for the marquee effect
    posters = [
        "https://image.tmdb.org/t/p/w500/9gk7adOG2ooPpcO1mAmJFAtefeO.jpg", # Inception
        "https://image.tmdb.org/t/p/w500/gEU2QniE6E77NI6lCU6MxlNBvIx.jpg", # Interstellar
        "https://image.tmdb.org/t/p/w500/qJ2tW6WMUDux911r6m7haRef0WH.jpg", # Dark Knight
        "https://image.tmdb.org/t/p/w500/pB8BM7pdSp6B6Ih7QZ4DrQ3PmJK.jpg", # Fight Club
        "https://image.tmdb.org/t/p/w500/f89U3ADr1oiB1s9GkdPOEpXUk5H.jpg", # Matrix
        "https://image.tmdb.org/t/p/w500/d5iIlFn5s0ImszYzBPbOYKQmG_1.jpg", # Pulp Fiction
        "https://image.tmdb.org/t/p/w500/q6y0Go1tsGEsmtFryDOJo3dEmqu.jpg", # Shawshank
        "https://image.tmdb.org/t/p/w500/3bhkrj58Vtu7enYsRolD1fZdja1.jpg", # Godfather
        "https://image.tmdb.org/t/p/w500/saHP97rTPS5eLmrLQEcANmKrsFl.jpg", # Forrest Gump
        "https://image.tmdb.org/t/p/w500/vQWk5YBFWFCPbV6sXl5EebieoT.jpg",  # Lord of the rings
        "https://image.tmdb.org/t/p/w500/oxcMhA1WlW3M2t8e6b12Y153Eok.jpg", # Avengers
        "https://image.tmdb.org/t/p/w500/8tZYtuWezp8JbcsvHYO0O46tFbo.jpg", # Joker
    ]
    
    # We duplicate the array 3 times to make sure it fills the screen perfectly for the loop
    images_html_fwd = "".join([f'<img class="marquee-img" src="{p}">' for p in posters * 3])
    images_html_rev = "".join([f'<img class="marquee-img" src="{p}">' for p in reversed(posters * 3)])

    st.markdown(f"""
<div class="splash-container">
    <div class="marquee-wrapper">
        <div class="marquee-row">{images_html_fwd}</div>
        <div class="marquee-row reverse">{images_html_rev}</div>
        <div class="marquee-row">{images_html_fwd}</div>
    </div>
    <div class="dark-overlay"></div>
    <div class="splash-text-box">
        <div class="h1-title">Assignment 2</div>
        <div class="h2-subtitle">Cloud recommender</div>
        <div class="h3-author">Zakaria Charouite</div>
    </div>
</div>
""", unsafe_allow_html=True)

    # 4.2 seconds delay gives enough time for the fade in, read, and fade out animations
    time.sleep(4.2)
    st.session_state.app_started = True
    st.rerun()
