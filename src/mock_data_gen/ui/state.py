"""Streamlit session state: template loading, schema rows and widget-state bookkeeping."""

import json
from copy import deepcopy
from itertools import count

import streamlit as st

from ..config import OUTPUT_DIR
from ..core import GENERATORS, validate_schema
from ..core.export import safe_name
from ..templates import TEMPLATES

BLANK_NAME = "Custom schema"
FIELD_KEYS = ("name", "type", "options", "null_pct")
DEFAULT_PASTE = (
    '{\n  "id": "uuid",\n  "email": "email",\n  "age": {"type": "integer", "options": "18,80"},\n'
    '  "plan": {"type": "choice", "options": "free:70|pro:25|team:5"}\n}'
)
_row_ids = count(1)


def new_rows(cols: list[dict]) -> list[dict]:
    """Attach a stable id to each column so its widgets keep their state when rows are removed."""
    return [{"name": c.get("name", ""), "type": c.get("type", "full_name"), "options": c.get("options", ""),
             "null_pct": float(c.get("null_pct", 0)), "id": next(_row_ids)} for c in cols]


def public_columns() -> list[dict]:
    return [{k: c[k] for k in FIELD_KEYS} for c in st.session_state.columns if str(c["name"]).strip()]


def schema_json(cols: list[dict]) -> str:
    """Compact `name: type` form, expanding only columns that carry options or nulls."""
    shape = {}
    for c in cols:
        extra = {k: c[k] for k in ("options", "null_pct") if c.get(k)}
        shape[c["name"]] = {"type": c["type"], **extra} if extra else c["type"]
    return json.dumps(shape, indent=2)


def sync_paste_box() -> None:
    s = st.session_state
    s.pasted_schema = schema_json(public_columns()) if s.kind == "schema" and public_columns() else DEFAULT_PASTE


def remember_baseline() -> None:
    """The schema as it was loaded; Reset fields returns to this."""
    st.session_state.baseline = deepcopy(public_columns())


def all_templates() -> dict[str, dict]:
    return {**TEMPLATES, **st.session_state.get("custom_templates", {})}


def init_state() -> None:
    s = st.session_state
    if "initialized" in s:
        return
    s.initialized = True
    s.custom_templates = {}
    s.rows = 1000
    s.limit = -1
    s.mode = "Generate once"
    s.buffer = 100_000
    s.seed = ""
    s.save_file = False
    s.save_dir = OUTPUT_DIR
    start_blank_schema()
    s.ds_name = "my_dataset"
    s.eps = 10


def load_template(name: str) -> None:
    s = st.session_state
    tpl = all_templates()[name]
    spec = tpl["spec"]
    s.template = name
    s.kind = spec["kind"]
    s.generator = spec.get("generator")
    s.columns = new_rows(spec.get("columns", []))
    s.ds_name = tpl["dataset"]
    s.eps = tpl["eps"]
    if s.kind == "generator":
        opts = {**GENERATORS[s.generator]["defaults"], **spec.get("options", {})}
        s.anomalies_pm = float(opts["anomalies_per_minute"])
        s.scenarios = list(opts["scenarios"])
    remember_baseline()
    sync_paste_box()


def start_blank_schema() -> None:
    s = st.session_state
    s.kind, s.generator = "schema", None
    s.template = BLANK_NAME
    s.columns = new_rows([
        {"name": "id", "type": "uuid"},
        {"name": "name", "type": "full_name"},
        {"name": "email", "type": "email"},
    ])
    remember_baseline()
    sync_paste_box()


def add_field() -> None:
    s = st.session_state
    s.columns += new_rows([{"name": f"field_{len(s.columns) + 1}", "type": "full_name"}])


def delete_field(field_id: int) -> None:
    s = st.session_state
    s.columns = [c for c in s.columns if c["id"] != field_id]


def reset_fields() -> None:
    s = st.session_state
    if s.kind == "generator":
        load_template(s.template)
        return
    s.columns = new_rows(s.baseline)
    sync_paste_box()


def save_as_template() -> None:
    s = st.session_state
    name = (s.get("tpl_save_name") or "").strip()
    cols = public_columns()
    if not name or not cols:
        s.tpl_save_msg = "Enter a name and keep at least one named field."
        return
    if name in TEMPLATES:
        name += " (custom)"
    s.custom_templates[name] = {
        "category": "Saved",
        "description": f"Your saved schema with {len(cols)} fields.",
        "dataset": safe_name(name), "eps": s.eps,
        "spec": {"kind": "schema", "columns": deepcopy(cols)},
    }
    s.template = name
    s.tpl_save_msg = f"Saved '{name}'. Find it on the Templates page."


def delete_custom_template(name: str) -> None:
    s = st.session_state
    s.custom_templates.pop(name, None)


def parse_pasted_schema(text: str) -> list[dict]:
    """Accepts a list of column objects, or an object mapping name -> type or name -> {type, options, null_pct}."""
    data = json.loads(text)
    if isinstance(data, dict):
        data = [{"name": k, **(v if isinstance(v, dict) else {"type": v})} for k, v in data.items()]
    if not isinstance(data, list) or not data:
        raise ValueError("expected a non-empty JSON list or object")
    cols = []
    for item in data:
        if not isinstance(item, dict) or "name" not in item:
            raise ValueError("each column needs a 'name'")
        cols.append({"name": str(item["name"]), "type": str(item.get("type", "")),
                     "options": str(item.get("options", "")), "null_pct": float(item.get("null_pct", 0))})
    bad = validate_schema(cols)
    if bad:
        raise ValueError("; ".join(bad))
    return cols


def apply_pasted_schema() -> None:
    s = st.session_state
    try:
        cols = parse_pasted_schema(s.pasted_schema)
    except (ValueError, TypeError) as exc:
        s.paste_error = f"Invalid schema: {exc}"
        return
    s.paste_error = None
    s.kind, s.generator = "schema", None
    s.columns = new_rows(cols)
    remember_baseline()


def current_spec() -> dict:
    s = st.session_state
    if s.kind == "generator":
        return {"kind": "generator", "generator": s.generator,
                "options": {"anomalies_per_minute": s.anomalies_pm, "scenarios": list(s.scenarios)}}
    return {"kind": "schema", "columns": public_columns()}


def keep_widget_state() -> None:
    # Streamlit drops state of widgets that are not rendered in a run (other page, hidden mode); keep it.
    for key in ("ds_name", "mode", "eps", "rows", "limit", "save_file", "save_format", "save_dir", "buffer", "seed",
                "anomalies_pm", "scenarios", "pasted_schema", "active_ds", "tpl_save_name"):
        if key in st.session_state:
            st.session_state[key] = st.session_state[key]
