from datetime import datetime

import pandas as pd
import streamlit as st

from ...config import API_PUBLIC_URL
from ...core import FORMATS, STORE, Dataset, serialize
from ..components import card_header, stop_stream


def metrics_and_preview(name: str) -> None:
    dataset = STORE.get(name)
    if dataset is None:
        st.info("Dataset was deleted.")
        return
    info = dataset.info()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total generated", f"{info['total_generated']:,}")
    c2.metric("Buffered for API", f"{info['buffered_rows']:,}")
    c3.metric("Status", "Streaming" if info["streaming"] else "Idle")
    c4.metric("Updated", datetime.now().strftime("%H:%M:%S"))
    if info["error"]:
        st.error(info["error"])
    if info["saved_path"]:
        st.caption(f"Saved to {info['saved_path']}")
    rows = dataset.all_rows()
    st.dataframe(pd.DataFrame(rows[-200:][::-1], columns=dataset.columns), height=380, width="stretch")


def export_view(dataset: Dataset) -> None:
    st.caption("Exports everything currently buffered in memory.")
    for col, fmt in zip(st.columns(len(FORMATS)), FORMATS):
        col.download_button(
            f"Download {fmt.upper()}",
            data=lambda fmt=fmt: serialize(dataset.all_rows(), dataset.columns, fmt, dataset.name),
            file_name=f"{dataset.name}.{fmt}", mime=FORMATS[fmt], width="stretch",
        )


def api_view(dataset: Dataset, api_ok: bool) -> None:
    base = API_PUBLIC_URL
    name = dataset.name
    if not api_ok:
        st.warning("The API server is not running, set MOCK_DATA_API_PORT to a free port and restart.")
    st.markdown(f"Interactive docs: [{base}/docs]({base}/docs)")
    st.code(
        f'curl "{base}/datasets/{name}/rows?limit=10"\n\n'
        f'# only rows newer than a previous response\'s "cursor"\n'
        f'curl "{base}/datasets/{name}/rows?after=<cursor>"\n\n'
        f'# other formats: csv, jsonl, sql\n'
        f'curl "{base}/datasets/{name}/rows?limit=1000&format=csv"\n\n'
        f'# control the dataset\n'
        f'curl -X POST "{base}/datasets/{name}/generate?rows=5000"\n'
        f'curl -X POST "{base}/datasets/{name}/stream/start"\n'
        f'curl -X POST "{base}/datasets/{name}/stream/stop"',
        language="bash",
    )
    st.code(
        'import requests\n\n'
        f'resp = requests.get("{base}/datasets/{name}/rows", params={{"limit": 100}}).json()\n'
        'rows, cursor = resp["data"], resp["cursor"]',
        language="python",
    )


def datasets_view() -> None:
    datasets = STORE.list()
    if not datasets:
        st.caption("No datasets yet.")
        return
    for dataset in datasets:
        info = dataset.info()
        c1, c2, c3, c4 = st.columns([4, 2, 1.2, 1.2], vertical_alignment="center")
        c1.markdown(f"**{info['name']}**  \n<span class='muted'>{len(info['columns'])} columns</span>",
                    unsafe_allow_html=True)
        c2.markdown(f"{info['total_generated']:,} rows  \n<span class='muted'>"
                    f"{'streaming' if info['streaming'] else 'idle'}</span>", unsafe_allow_html=True)
        if info["streaming"]:
            c3.button("Stop", key=f"stop_{info['name']}", on_click=stop_stream, args=(info["name"],), width="stretch")
        if c4.button("Delete", key=f"rmds_{info['name']}", width="stretch"):
            STORE.delete(info["name"])
            st.rerun()


def render(api_ok: bool) -> None:
    s = st.session_state
    names = [d.name for d in STORE.list()]
    with st.container(border=True, key="card_results"):
        card_header(3, "Preview & Export", "Inspect the data, download it, or read it from the API.")
        if not names:
            st.markdown('<div class="muted">Nothing generated yet. Configure a dataset and press Generate.</div>',
                        unsafe_allow_html=True)
            return
        if s.get("active_ds") not in names:
            s.active_ds = names[0]
        a, b, _ = st.columns([2, 1, 3], vertical_alignment="bottom")
        name = a.selectbox("Dataset", names, key="active_ds")
        dataset = STORE.get(name)
        if dataset.streaming:
            b.button("Stop streaming", key="stop_active", on_click=stop_stream, args=(name,), width="stretch")
        preview_tab, export_tab, api_tab, all_tab = st.tabs(["Preview", "Export", "API", "All datasets"])
        with preview_tab:
            panel = st.fragment(metrics_and_preview, run_every=1.5 if dataset.streaming else None)
            panel(name)
        with export_tab:
            export_view(dataset)
        with api_tab:
            api_view(dataset, api_ok)
        with all_tab:
            datasets_view()
