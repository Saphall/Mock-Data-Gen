"""Streamlit entry point, launched by `mock-data-gen` (see cli.py)."""

from pathlib import Path

import streamlit as st

from mock_data_gen.api import start_api
from mock_data_gen.config import API_HOST, API_PORT
from mock_data_gen.ui import nav, state
from mock_data_gen.ui.components import streams_banner
from mock_data_gen.ui.theme import build_css, current_mode, toggle_mode

ASSETS = Path(__file__).parent / "assets"

st.set_page_config(page_title="MockData Gen", page_icon=str(ASSETS / "icon.svg"), layout="wide",
                   initial_sidebar_state="collapsed")


def main() -> None:
    mode = current_mode()
    st.markdown(build_css(mode), unsafe_allow_html=True)
    st.logo(str(ASSETS / ("logo-light.svg" if mode == "light" else "logo.svg")), size="large")
    with st.container(key="theme_toggle"):
        st.button(":material/light_mode: Light" if mode == "dark" else ":material/dark_mode: Dark",
                  key="theme_btn", on_click=toggle_mode, help="Switch between dark and light theme")
    state.init_state()
    state.keep_widget_state()
    st.session_state.api_status = start_api(API_HOST, API_PORT)
    page = st.navigation([nav.HOME_PAGE, nav.TEMPLATES_PAGE, nav.DOCS_PAGE], position="top")
    streams_banner()
    page.run()


main()
