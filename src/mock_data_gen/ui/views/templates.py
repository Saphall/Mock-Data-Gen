import streamlit as st

from ...templates import CATEGORIES
from ..components import page_header
from ..state import all_templates, delete_custom_template, load_template

SAVED = "Saved"


def _card(name: str, tpl: dict, selected: bool, key: str) -> None:
    from ..nav import HOME_PAGE

    spec = tpl["spec"]
    if spec["kind"] == "generator":
        chips = '<span class="chip">built-in generator</span>'
    else:
        names = [c["name"] for c in spec["columns"]]
        chips = "".join(f'<span class="chip">{n}</span>' for n in names[:3])
        if len(names) > 3:
            chips += f'<span class="chip">+{len(names) - 3}</span>'
    deletable = tpl.get("category") == SAVED
    with st.container(key=f"{'tplcard_sel' if selected else 'tplcard'}_{key}"):
        st.markdown(f'<div class="tpl-name">{name}</div><div class="tpl-desc">{tpl["description"]}</div>'
                    f'<div class="chips">{chips}</div>', unsafe_allow_html=True)
        use, drop = st.columns([4, 1]) if deletable else (st.container(), None)
        if use.button("Use template", key=f"tpl_{key}", width="stretch",
                      type="primary" if selected else "secondary"):
            load_template(name)
            st.switch_page(HOME_PAGE)
        if drop is not None:
            drop.button("×", key=f"del_tpl_{key}", help="Delete template", on_click=delete_custom_template,
                        args=(name,), width="stretch")


def render() -> None:
    page_header("Template Gallery", "Start from a ready-made dataset. Picking one loads it into the builder, "
                                    "where you can edit it.")
    templates = all_templates()
    categories = ["All", *CATEGORIES]
    if any(t.get("category") == SAVED for t in templates.values()):
        categories.insert(1, SAVED)

    query = st.text_input("Search templates", placeholder="Search templates...", label_visibility="collapsed")
    chosen = st.pills("Category", categories, default="All", key="tpl_cat", label_visibility="collapsed") or "All"
    needle = query.strip().lower()
    items = sorted(
        ((n, t) for n, t in templates.items()
         if (chosen == "All" or t.get("category") == chosen)
         and (not needle or needle in f"{n} {t['description']} {t.get('category', '')}".lower())),
        key=lambda item: item[0].lower(),
    )

    selected = st.session_state.get("template")
    for start in range(0, len(items), 3):
        for col, (name, tpl) in zip(st.columns(3), items[start:start + 3]):
            with col:
                _card(name, tpl, name == selected, f"{start}_{name}")
    if not items:
        st.caption("No templates match.")
    st.caption(f"{len(templates)} templates available · Click to load into the builder")
