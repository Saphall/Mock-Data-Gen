import streamlit as st

from ...config import API_ENABLED, API_PUBLIC_URL
from ...core import FIELD_TYPES, FORMATS
from ...templates import TEMPLATES

STEPS = ("Schema", "Configure", "Preview &amp; Export")


def topbar(api_ok: bool, api_msg: str) -> None:
    if not API_ENABLED:
        status = '<span class="pill">API disabled on this host</span>'
    else:
        status = (f'<span class="pill ok">API live &middot; <b>{API_PUBLIC_URL}</b></span>' if api_ok
              else f'<span class="pill bad">API offline &middot; {api_msg}</span>')
    step_html = '<span class="line"></span>'.join(f'<span class="step"><i>{n}</i>{name}</span>'
                                                  for n, name in enumerate(STEPS, 1))
    st.markdown(
        f"""<div class="topbar">
          <div class="steps">{step_html}</div>
          <div>{status}</div>
        </div>""",
        unsafe_allow_html=True,
    )


def intro() -> None:
    st.markdown(
        f"""<div class="hero">
          <h1>Free mock data generator with a live API</h1>
          <p>Build a schema from {len(FIELD_TYPES)} data types, generate a batch or stream events at a fixed rate,
          then let other services read them over HTTP or save them to files.</p>
          <span class="pill">Runs locally</span><span class="pill">{len(TEMPLATES)} ready-made templates</span>
          <span class="pill">Export {' &middot; '.join(f.upper() for f in FORMATS)}</span>
        </div>""",
        unsafe_allow_html=True,
    )
