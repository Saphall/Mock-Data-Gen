import streamlit as st

from ..sections import configure, hero, results, schema


def render() -> None:
    hero.topbar(*st.session_state.api_status)
    hero.intro()
    schema.render()
    configure.render()
    results.render(st.session_state.api_status[0])
