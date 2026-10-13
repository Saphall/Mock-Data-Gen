import streamlit as st

from ...config import API_ENABLED
from ...core import FORMATS, MAX_ROWS_ONCE, STORE, Dataset, validate_schema
from ..components import card_header
from ..state import current_spec


def run_generation(streaming: bool, rows: int, limit: int, save: dict | None, buffer: int, seed_text: str) -> None:
    s = st.session_state
    spec = current_spec()
    if spec["kind"] == "schema":
        errors = validate_schema(spec["columns"])
        if not spec["columns"]:
            errors.append("add at least one column")
        if errors:
            st.error("Fix the schema first: " + "; ".join(errors))
            return
    try:
        seed = int(seed_text) if seed_text.strip() else None
        dataset = Dataset(s.ds_name, spec, eps=s.eps, limit=limit, buffer=buffer, save=save, seed=seed)
        if streaming:
            STORE.put(dataset).start_stream()
        else:
            with st.spinner("Generating..."):
                count = STORE.put(dataset).generate(rows)
            st.toast(f"Generated {count:,} rows")
    except ValueError as exc:
        st.error(str(exc))
        return
    s.active_ds = dataset.name


def render() -> None:
    s = st.session_state
    with st.container(border=True, key="card_configure"):
        card_header(2, "Configure", "Choose how much to generate and where the data goes.")
        c1, c2, c3 = st.columns(3, gap="large")
        with c1:
            st.text_input("Dataset name", key="ds_name", help="Used in the API path and as the file name.")
            st.segmented_control("Mode", ["Generate once", "Stream continuously"], key="mode", width="stretch")
        streaming = st.session_state.mode == "Stream continuously"

        rows, limit = 0, -1
        with c2:
            if streaming:
                st.number_input("Events per second", 1, 5000, key="eps")
                limit = st.number_input("Row limit (-1 = unlimited)", -1, 100_000_000, key="limit")
            else:
                rows = st.number_input("Rows", 1, MAX_ROWS_ONCE, step=100, key="rows")
                st.number_input("Simulated events per second", 1, 5000, key="eps",
                                help="Spreads timestamps as if rows arrived at this rate.")

        save = None
        with c3:
            if API_ENABLED:
                st.checkbox("Expose through API", value=True, disabled=True,
                            help="Every dataset is readable over HTTP while the app is running.")
            else:
                st.caption("HTTP API unavailable on this host; use the Export tab.")
            if st.checkbox("Also save to a file", key="save_file"):
                formats = ["csv", "jsonl", "sql"] if streaming else list(FORMATS)
                if s.get("save_format") not in formats:
                    s.save_format = formats[0]
                fmt = st.selectbox("Format", formats, key="save_format")
                directory = st.text_input("Directory", key="save_dir")
                save = {"format": fmt, "directory": directory}

        with st.expander("Advanced"):
            a, b = st.columns(2)
            buffer = a.number_input("API buffer (most recent rows kept in memory)", 1000, 5_000_000,
                                    step=1000, key="buffer")
            seed_text = b.text_input("Random seed (optional)", key="seed")

        running = STORE.get(s.ds_name)
        label = "Start streaming" if streaming else "Generate"
        a, b, _ = st.columns([2, 1, 4])
        go = a.button(label, type="primary", width="stretch")
        stop = b.button("Stop", width="stretch", disabled=not (running and running.streaming))

        if stop and running:
            running.stop_stream()
        if go:
            run_generation(streaming, rows, int(limit), save, int(buffer), seed_text)
