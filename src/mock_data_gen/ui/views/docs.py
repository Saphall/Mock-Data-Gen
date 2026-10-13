import html
import re
from datetime import datetime, timezone

import streamlit as st

from ...config import API_PUBLIC_URL
from ...core import FIELD_TYPES, GROUPS
from ...core.fields import build_producer
from ..components import page_header


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


@st.cache_data(show_spinner=False)
def _examples() -> dict[str, str]:
    now = datetime.now(timezone.utc)
    out = {}
    for key in FIELD_TYPES:
        try:
            value = "(your value)" if key == "static" else str(build_producer(key, "")(now))
        except Exception:  # an example is decoration; never fail the docs page for it
            value = ""
        out[key] = value if len(value) <= 52 else value[:49] + "..."
    return out


def _type_table(group: str) -> str:
    examples = _examples()
    rows = "".join(
        f"<tr><td><b>{html.escape(t.title)}</b><br><code>{t.key}</code></td><td>{html.escape(t.desc)}</td>"
        f"<td>{'<code>' + html.escape(t.hint) + '</code>' if t.hint else '&ndash;'}</td>"
        f"<td><code>{html.escape(examples[t.key])}</code></td></tr>"
        for t in GROUPS[group]
    )
    return ('<table class="doc-table"><thead><tr><th>Type</th><th>Description</th><th>Options</th><th>Example</th>'
            f"</tr></thead><tbody>{rows}</tbody></table>")


def render() -> None:
    page_header("Documentation", "Column types, option syntax and the HTTP API.")
    toc, body = st.columns([1, 4], gap="large")

    with toc, st.container(border=True, key="card_doc_toc"):
        st.markdown('<div class="col-label">On this page</div>', unsafe_allow_html=True)
        st.markdown("\n".join(
            ["- [Column types](#column-types)", *(f"    - [{g}](#{_slug(g)})" for g in GROUPS),
             "- [Options syntax](#options-syntax)", "- [HTTP API](#http-api)", "- [Configuration](#configuration)"]))

    with body:
        with st.container(border=True, key="card_docs_types"):
            st.markdown("## Column types")
            st.markdown(f"{len(FIELD_TYPES)} types in {len(GROUPS)} categories. Pick one with the type button in the "
                        "builder; the **Options** column shows what its options box accepts.")
            for group in GROUPS:
                st.markdown(f"### {group}")
                st.markdown(_type_table(group), unsafe_allow_html=True)

        with st.container(border=True, key="card_docs_options"):
            st.markdown("## Options syntax")
            st.markdown(
                "| Where | Format | Example |\n| --- | --- | --- |\n"
                "| Ranges | `min,max` | `integer` &rarr; `1,100` |\n"
                "| Time ranges | ISO date, `now`, or an offset in `s m h d w` | `datetime` &rarr; `-7d,now` |\n"
                "| Weighted choice | `value:weight` separated by `\\|` | `choice` &rarr; `free:70\\|pro:25\\|team:5` |\n"
                "| Sequences | `start,step` | `sequence` &rarr; `1000,1` |\n"
                "| Null % | share of rows that become `null` | `10` |"
            )
            st.markdown("Pasted schemas accept a list of columns or a `name: type` object:")
            st.code('{\n  "id": "uuid",\n  "age": {"type": "integer", "options": "18,80", "null_pct": 5}\n}',
                    language="json")

        with st.container(border=True, key="card_docs_api"):
            st.markdown("## HTTP API")
            st.markdown(
                f"Every dataset is served at `{API_PUBLIC_URL}` while the app runs. Interactive docs: "
                f"[{API_PUBLIC_URL}/docs]({API_PUBLIC_URL}/docs).\n\n"
                "| Method | Path | Purpose |\n| --- | --- | --- |\n"
                "| GET | `/datasets` | List datasets |\n"
                "| GET | `/datasets/{name}/rows?limit=&offset=&after=&format=` | Read rows as `json`, `csv`, `jsonl` or "
                "`sql`; pass the returned `cursor` as `after` to get only newer rows |\n"
                "| POST | `/datasets` | Create a dataset from a spec |\n"
                "| POST | `/datasets/{name}/generate?rows=` | Regenerate a dataset |\n"
                "| POST | `/datasets/{name}/stream/start` or `/stop` | Control streaming |\n"
                "| DELETE | `/datasets/{name}` | Remove a dataset |"
            )

        with st.container(border=True, key="card_docs_config"):
            st.markdown("## Configuration")
            st.markdown(
                "| Variable | Default | Purpose |\n| --- | --- | --- |\n"
                "| `MOCK_DATA_API_HOST` | `127.0.0.1` | API bind address |\n"
                "| `MOCK_DATA_API_PORT` | `8000` | API port |\n"
                "| `MOCK_DATA_API_PUBLIC_URL` | `http://localhost:<port>` | URL shown in the UI |\n"
                "| `MOCK_DATA_OUTPUT_DIR` | `output` | Default folder for saved files |"
            )
