"""Page registry; page objects are module-level so they stay stable across Streamlit reruns."""

import streamlit as st

from .views import docs, home, templates

HOME_PAGE = st.Page(home.render, title="Builder", default=True)
TEMPLATES_PAGE = st.Page(templates.render, title="Templates", url_path="templates")
DOCS_PAGE = st.Page(docs.render, title="Docs", url_path="docs")
