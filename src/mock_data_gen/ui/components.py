import streamlit as st

from ..core import STORE


def card_header(number: int, title: str, subtitle: str) -> None:
    st.markdown(
        f'<div class="card-head"><span class="badge">{number}</span><div>'
        f'<div class="card-title">{title}</div><div class="muted">{subtitle}</div></div></div>',
        unsafe_allow_html=True,
    )


def page_header(title: str, subtitle: str) -> None:
    st.markdown(f'<div class="hero"><h1>{title}</h1><p>{subtitle}</p></div>', unsafe_allow_html=True)


def stop_stream(name: str) -> None:
    dataset = STORE.get(name)
    if dataset:
        dataset.stop_stream()


def _streams() -> None:
    running = [d for d in STORE.list() if d.streaming]
    if not running:
        return
    with st.container(key="stream_banner"):
        for dataset in running:
            text, stop = st.columns([6, 1], vertical_alignment="center")
            text.markdown(f'<span class="live-dot"></span>Streaming <b>{dataset.name}</b> &middot; '
                          f'{dataset.total:,} rows &middot; {dataset.eps}/s', unsafe_allow_html=True)
            if stop.button("Stop", key=f"stopbar_{dataset.name}", width="stretch"):
                stop_stream(dataset.name)
                st.rerun()


def streams_banner() -> None:
    """Shown on every page so a running stream can always be stopped."""
    live = any(d.streaming for d in STORE.list())
    st.fragment(_streams, run_every=2 if live else None)()
