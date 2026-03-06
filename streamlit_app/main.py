import os
import streamlit as st
from dotenv import load_dotenv

if os.path.exists('.env'):
    load_dotenv('.env')
elif os.path.exists('../.env'):
    load_dotenv(dotenv_path='../.env')

st.set_page_config(page_title="Assignment 1 Movies", page_icon="🎬", layout="wide")

from ui.styles import apply_custom_styles
from views.landing import show_landing_page
from views.catalog import show_catalog_page
from views.movie_detail import show_movie_detail_page

def main():
    apply_custom_styles()
    
    if "app_started" not in st.session_state:
        st.session_state.app_started = False
        
    if not st.session_state.app_started:
        show_landing_page()
        return
    
    if "view_movie_id" in st.session_state:
        show_movie_detail_page(st.session_state.view_movie_id)
        return

    show_catalog_page()

if __name__ == '__main__':
    main()
