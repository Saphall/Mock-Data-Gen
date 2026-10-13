import html
import json

import pandas as pd
import streamlit as st

from ...core import FIELD_TYPES, GENERATORS, GROUPS
from ..components import card_header
from ..state import (
    BLANK_NAME, add_field, apply_pasted_schema, delete_field, public_columns, reset_fields, save_as_template,
    start_blank_schema,
)

FIELD_COLS = [2.4, 2.0, 2.6, 1.9, 0.5]
GROUP_ICONS = {
    "Person": "person", "Location": "location_on", "Finance": "account_balance_wallet", "Internet": "language",
    "Commerce": "shopping_cart", "Date & Time": "schedule", "Numbers": "tag", "Text": "text_fields",
    "Tech": "terminal", "Custom": "tune",
}


def generator_view() -> None:
    s = st.session_state
    entry = GENERATORS[s.generator]
    st.markdown(f"**{entry['label']}** is a built-in generator with a fixed set of columns and attack scenarios.")
    st.dataframe(pd.DataFrame({"column": entry["columns"]}), hide_index=True, height=250, width="stretch")
    a, b = st.columns([1, 2])
    a.number_input("Anomaly bursts per minute", 0.0, 600.0, step=0.5, key="anomalies_pm")
    b.multiselect("Attack scenarios", entry["scenarios"], key="scenarios")
    st.button("Switch to a custom schema", on_click=start_blank_schema)


def _pick_body(fid: int) -> None:
    col = next(c for c in st.session_state.columns if c["id"] == fid)
    query = st.text_input("Search types", key=f"q_{fid}", placeholder=f"Search {len(FIELD_TYPES)} types...",
                          label_visibility="collapsed").strip().lower()
    found = False
    with st.container(height=600, border=False, key=f"pick_list_{fid}"):
        for index, (group, types) in enumerate(GROUPS.items()):
            matches = [t for t in types if not query or query in f"{t.key} {t.title} {t.desc} {group}".lower()]
            if not matches:
                continue
            found = True
            with st.container(key=f"dlg_group_{fid}_{index}"):
                st.markdown(f":material/{GROUP_ICONS.get(group, 'category')}:&nbsp; {group}")
            for start in range(0, len(matches), 2):
                for cell, t in zip(st.columns(2), matches[start:start + 2]):
                    current = t.key == col["type"]
                    picked = cell.button(t.title, key=f"pick_{fid}_{t.key}", help=t.desc, width="stretch",
                                         icon=":material/check:" if current else None,
                                         type="primary" if current else "secondary")
                    if picked:
                        if t.key != col["type"]:
                            col["type"], col["options"] = t.key, ""
                        st.rerun()
    if not found:
        st.caption("No types match your search.")


def open_type_dialog(fid: int, name: str) -> None:
    # The native title is hidden by CSS so the field name can be coloured.
    @st.dialog("Select type", width="small")
    def dialog() -> None:
        st.markdown(f'<div class="dlg-title">Select type for <span class="dlg-field">{html.escape(name or "field")}'
                    "</span></div>", unsafe_allow_html=True)
        _pick_body(fid)

    dialog()


def field_row(col: dict) -> None:
    fid = col["id"]
    c_name, c_type, c_opt, c_null, c_del = st.columns(FIELD_COLS, vertical_alignment="center")
    col["name"] = c_name.text_input("Field name", col["name"], key=f"name_{fid}", placeholder="field_name",
                                    label_visibility="collapsed")
    ftype = FIELD_TYPES[col["type"]]
    if c_type.button(ftype.title, key=f"typebtn_{fid}", icon=":material/unfold_more:", width="stretch",
                     help=f"{ftype.group}: {ftype.desc}"):
        open_type_dialog(fid, col["name"])

    if ftype.hint:
        col["options"] = c_opt.text_input("Options", col["options"], key=f"opt_{fid}_{ftype.key}",
                                          placeholder=ftype.hint, label_visibility="collapsed")
    else:
        col["options"] = ""
        c_opt.text_input("Options", "", key=f"opt_off_{fid}", placeholder="no options", disabled=True,
                         label_visibility="collapsed")
    col["null_pct"] = float(c_null.slider("Null %", 0, 100, int(col["null_pct"]), 5, format="%d%%",
                                          key=f"null_{fid}", label_visibility="collapsed"))
    c_del.button("×", key=f"del_{fid}", on_click=delete_field, args=(fid,), help="Remove field", width="stretch")


def builder_view() -> None:
    from ..nav import DOCS_PAGE

    s = st.session_state
    labels = st.columns(FIELD_COLS)
    for label, text in zip(labels, ["Field name", "Type", "Options", "Null %", ""]):
        label.markdown(f'<div class="col-label">{text}</div>', unsafe_allow_html=True)
    with st.container(key="fields"):
        for col in list(s.columns):
            field_row(col)

    a, b, c, d, e = st.columns([1.4, 1.4, 1.9, 2.3, 2.1], vertical_alignment="center")
    a.button("+ Add field", on_click=add_field, width="stretch")
    b.button("Reset fields", on_click=reset_fields, width="stretch")
    with c.popover("Save as template", width="stretch"):
        st.text_input("Template name", key="tpl_save_name", placeholder="My schema")
        st.button("Save", on_click=save_as_template, type="primary")
        if s.get("tpl_save_msg"):
            st.caption(s.tpl_save_msg)
    if s.template != BLANK_NAME:
        d.button("Switch to custom schema", on_click=start_blank_schema, width="stretch")
    with e.container(key="docs_link"):
        st.page_link(DOCS_PAGE, label="Column type reference")

    with st.expander("Paste a JSON schema"):
        st.text_area("Schema JSON", key="pasted_schema", height=200,
                     help="A list of {name, type, options, null_pct} or a {name: type} object.")
        st.button("Apply schema", on_click=apply_pasted_schema, type="primary")
        if s.get("paste_error"):
            st.error(s.paste_error)
    with st.expander("Schema as JSON"):
        st.code(json.dumps(public_columns(), indent=2), language="json")


def render() -> None:
    from ..nav import TEMPLATES_PAGE

    with st.container(border=True, key="card_schema"):
        card_header(1, "Schema", "Add fields and pick a data type for each.")
        a, b = st.columns([3, 1], vertical_alignment="center")
        a.markdown(f'<div class="muted">Current template: <b>{st.session_state.template}</b></div>',
                   unsafe_allow_html=True)
        b.page_link(TEMPLATES_PAGE, label="Browse templates")
        if st.session_state.kind == "generator":
            generator_view()
        else:
            builder_view()
