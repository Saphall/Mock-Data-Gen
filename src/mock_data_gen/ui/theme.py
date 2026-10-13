"""Light and dark palettes. The mode lives in Streamlit's own theme config so native widgets follow it too."""

import streamlit as st
from streamlit import config

# Streamlit theme options, applied through `config.set_option("theme.<key>", ...)`.
THEME_OPTIONS = {
    "dark": {"base": "dark", "primaryColor": "#8b5cf6", "backgroundColor": "#151c38",
             "secondaryBackgroundColor": "#1e2748", "textColor": "#e8ecf8"},
    "light": {"base": "light", "primaryColor": "#7c3aed", "backgroundColor": "#dde2f1",
              "secondaryBackgroundColor": "#cdd4ea", "textColor": "#1b2140"},
}

PALETTES = {
    "dark": {
        "bg": "#151c38", "bg-header": "rgba(21,28,56,.74)", "grid": "rgba(255,255,255,.03)",
        "glow1": "rgba(139,92,246,.5)", "glow2": "rgba(14,165,233,.42)", "glow3": "rgba(236,72,153,.3)",
        "card-1": "rgba(22,30,64,.92)", "card-2": "rgba(14,21,48,.9)", "card-border": "rgba(255,255,255,.14)",
        "card-shadow": "0 12px 44px rgba(0,0,0,.28)", "card-inset": "rgba(255,255,255,.12)",
        "surface": "rgba(255,255,255,.06)", "surface-soft": "rgba(255,255,255,.04)",
        "surface-hover": "rgba(255,255,255,.08)", "tile": "rgba(13,19,44,.6)",
        "border": "rgba(255,255,255,.13)", "border-strong": "rgba(255,255,255,.2)", "border-soft": "rgba(255,255,255,.1)",
        "text": "#e8ecf8", "text-strong": "#f3f5ff", "text-muted": "#9aa4c2", "text-dim": "#8f99b8",
        "text-soft": "#aab3cf", "text-code": "#7dd3fc", "code-bg": "rgba(255,255,255,.07)",
        "dialog-bg": "#1b2346", "field-color": "#2db36f", "accent-title": "#c4b5fd",
        "hero-grad": "linear-gradient(90deg, #c4b5fd, #7dd3fc 60%, #f9a8d4)",
        "pill-ok": "#a7f3d0", "pill-bad": "#fecaca", "danger": "#fca5a5",
        "scroll-thumb": "rgba(255,255,255,.25)", "scroll-track": "rgba(255,255,255,.05)",
    },
    "light": {
        "bg": "#dde2f1", "bg-header": "rgba(221,226,241,.82)", "grid": "rgba(30,41,90,.05)",
        "glow1": "rgba(139,92,246,.26)", "glow2": "rgba(14,165,233,.22)", "glow3": "rgba(236,72,153,.14)",
        "card-1": "rgba(243,245,252,.92)", "card-2": "rgba(232,236,248,.9)", "card-border": "rgba(30,41,90,.2)",
        "card-shadow": "0 12px 40px rgba(60,70,140,.14)", "card-inset": "rgba(255,255,255,.95)",
        "surface": "rgba(255,255,255,.95)", "surface-soft": "rgba(30,41,90,.04)",
        "surface-hover": "rgba(30,41,90,.07)", "tile": "rgba(255,255,255,.7)",
        "border": "rgba(30,41,90,.16)", "border-strong": "rgba(30,41,90,.28)", "border-soft": "rgba(30,41,90,.1)",
        "text": "#1b2140", "text-strong": "#0f1535", "text-muted": "#5a6385", "text-dim": "#6b7396",
        "text-soft": "#46506f", "text-code": "#0369a1", "code-bg": "rgba(30,41,90,.07)",
        "dialog-bg": "#f3f5fb", "field-color": "#15803d", "accent-title": "#6d28d9",
        "hero-grad": "linear-gradient(90deg, #7c3aed, #0284c7 60%, #db2777)",
        "pill-ok": "#047857", "pill-bad": "#b91c1c", "danger": "#dc2626",
        "scroll-thumb": "rgba(30,41,90,.3)", "scroll-track": "rgba(30,41,90,.06)",
    },
}


def current_mode() -> str:
    return "light" if st.get_option("theme.base") == "light" else "dark"


def toggle_mode() -> None:
    for key, value in THEME_OPTIONS["light" if current_mode() == "dark" else "dark"].items():
        config.set_option(f"theme.{key}", value)


def build_css(mode: str) -> str:
    variables = "".join(f"--{name}: {value};" for name, value in PALETTES[mode].items())
    return f"<style>:root {{ {variables} }}{_RULES}</style>"


_RULES = """
.stApp, .stApp p, .stApp label, .stApp button, .stApp input, .stApp textarea, .stApp h1, .stApp h2, .stApp h3 {
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
}
.stApp {
  background:
    linear-gradient(var(--grid) 1px, transparent 1px) 0 0 / 56px 56px,
    linear-gradient(90deg, var(--grid) 1px, transparent 1px) 0 0 / 56px 56px,
    radial-gradient(1000px 560px at 6% -8%, var(--glow1), transparent 62%),
    radial-gradient(900px 520px at 98% 2%, var(--glow2), transparent 62%),
    radial-gradient(900px 600px at 50% 118%, var(--glow3), transparent 62%),
    var(--bg);
  background-attachment: fixed;
}
header[data-testid="stHeader"] { background: var(--bg-header); backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px); border-bottom: 1px solid var(--border-soft); }
#MainMenu, footer { visibility: hidden; }
.block-container { max-width: 1280px; padding-top: 4rem; padding-bottom: 3rem; }

/* theme switch, pinned into the navbar */
[class*="st-key-theme_toggle"] { position: fixed; top: .5rem; right: 1.2rem; z-index: 1000002; width: auto; }
[class*="st-key-theme_toggle"] button { min-height: 2.2rem; padding: 0 .9rem; }

/* glass surfaces */
[class*="st-key-card_"], .topbar {
  background: linear-gradient(160deg, var(--card-1), var(--card-2));
  backdrop-filter: blur(22px) saturate(140%); -webkit-backdrop-filter: blur(22px) saturate(140%);
  border: 1px solid var(--card-border) !important;
  border-radius: 20px;
  box-shadow: var(--card-shadow), inset 0 1px 0 var(--card-inset);
}
[class*="st-key-card_"] { padding: 1.5rem 1.7rem 1.6rem !important; gap: 1rem; }

/* top bar */
.topbar { display: flex; align-items: center; justify-content: space-between; gap: 1rem; padding: .7rem 1.1rem;
  margin-bottom: 1.8rem; flex-wrap: wrap; }
.topbar > div:last-child { margin-left: auto; }
.steps { display: flex; align-items: center; gap: .55rem; color: var(--text-soft); font-size: .88rem; }
.steps .step { display: inline-flex; align-items: center; gap: .45rem; }
.steps .step i { font-style: normal; width: 1.45rem; height: 1.45rem; border-radius: 50%; display: inline-flex;
  align-items: center; justify-content: center; font-size: .75rem; font-weight: 700; color: #fff;
  background: linear-gradient(135deg, #8b5cf6, #0ea5e9); }
.steps .line { width: 1.6rem; height: 1px; background: var(--border-strong); }

/* hero */
.hero { margin-bottom: 1.3rem; }
.hero h1 { font-size: 2.35rem; line-height: 1.12; margin: 0 0 .5rem 0; font-weight: 800; letter-spacing: -.025em;
  padding: 0; background: var(--hero-grad); -webkit-background-clip: text; background-clip: text; color: transparent; }
.hero p { color: var(--text-soft); font-size: 1rem; max-width: 780px; margin: 0 0 .9rem 0; }
.pill { display: inline-block; padding: .26rem .75rem; margin: 0 .45rem .4rem 0; border-radius: 999px; font-size: .8rem;
  background: var(--surface-hover); border: 1px solid var(--border); color: var(--text-soft); }
.pill b { color: var(--text-strong); }
.pill.ok { border-color: rgba(52,211,153,.6); color: var(--pill-ok); background: rgba(52,211,153,.1); }
.pill.bad { border-color: rgba(248,113,113,.6); color: var(--pill-bad); background: rgba(248,113,113,.1); }

/* card header */
.card-head { display: flex; align-items: center; gap: .75rem; margin-bottom: .6rem; }
.card-head .badge { width: 2rem; height: 2rem; border-radius: 10px; display: inline-flex; align-items: center;
  justify-content: center; font-weight: 700; color: #fff; background: linear-gradient(135deg, #8b5cf6, #0ea5e9);
  box-shadow: 0 4px 16px rgba(99,102,241,.4); flex: none; }
.card-title { font-size: 1.12rem; font-weight: 700; color: var(--text-strong); line-height: 1.2; }
.muted { color: var(--text-muted); font-size: .86rem; }
.col-label { color: var(--text-dim); font-size: .72rem; text-transform: uppercase; letter-spacing: .08em; font-weight: 600; }
.section-title { font-size: 1.05rem; font-weight: 700; color: var(--text-strong); margin: 1.6rem 0 .8rem; }

/* inputs */
div[data-baseweb="input"], div[data-baseweb="base-input"], div[data-baseweb="select"] > div, textarea {
  background: var(--surface) !important; border-color: var(--border) !important; border-radius: 10px !important;
}
div[data-baseweb="input"]:focus-within, div[data-baseweb="select"] > div:focus-within, textarea:focus {
  border-color: rgba(139,92,246,.85) !important; box-shadow: 0 0 0 3px rgba(139,92,246,.18);
}
div[data-testid="stDataFrame"] { border: 1px solid var(--border); border-radius: 12px; overflow: hidden; }
div[data-testid="stExpander"] details { background: var(--surface-soft); border: 1px solid var(--border-soft) !important;
  border-radius: 12px; }
[data-testid="stSliderTickBarMin"], [data-testid="stSliderTickBarMax"] { display: none; }

/* buttons */
.stButton > button, .stDownloadButton > button, [data-testid="stPopover"] > button {
  border-radius: 12px; border: 1px solid var(--border); background: var(--surface-hover); color: var(--text);
  transition: all .15s ease;
}
.stButton > button:hover, .stDownloadButton > button:hover, [data-testid="stPopover"] > button:hover {
  border-color: rgba(139,92,246,.85); background: rgba(139,92,246,.2); color: var(--text-strong);
}
.stButton > button[kind="primary"] {
  background: linear-gradient(135deg, #8b5cf6, #0ea5e9); border: 0; color: #fff; font-weight: 600;
  box-shadow: 0 6px 24px rgba(99,102,241,.45);
}
.stButton > button[kind="primary"]:hover { filter: brightness(1.12); transform: translateY(-1px); color: #fff; }
[class*="st-key-fields"] { gap: .45rem; }
[class*="st-key-del_"] button { padding: 0; min-height: 2.4rem; color: var(--danger); }
[class*="st-key-del_"] button:hover { border-color: rgba(248,113,113,.8); background: rgba(248,113,113,.18); }
[class*="st-key-rmds_"] button { color: var(--danger); border-color: rgba(248,113,113,.4); }
[class*="st-key-rmds_"] button:hover { border-color: rgba(248,113,113,.85); background: rgba(248,113,113,.16); }
[class*="st-key-typebtn_"] button { justify-content: space-between; }

/* tabs and metrics */
button[data-baseweb="tab"] { background: transparent; border-radius: 10px 10px 0 0; }
div[data-baseweb="tab-highlight"] { background: linear-gradient(90deg, #8b5cf6, #0ea5e9); }
div[data-testid="stTabs"] { margin-top: .6rem; }
div[data-testid="stTabsContent"], div[role="tabpanel"] { padding-top: 1rem; }
div[data-testid="stMetric"] { background: var(--surface-soft); border: 1px solid var(--border-soft);
  border-radius: 14px; padding: .8rem 1.1rem; }
div[data-testid="stMetricLabel"] p { font-size: .8rem; color: var(--text-muted); }
div[data-testid="stMetricValue"] { font-size: 1.6rem; }

/* running stream banner */
[class*="st-key-stream_banner"] { background: rgba(52,211,153,.1); border: 1px solid rgba(52,211,153,.45);
  border-radius: 14px; padding: .6rem 1rem; margin-bottom: 1rem; gap: .4rem; }
.live-dot { display: inline-block; width: .6rem; height: .6rem; border-radius: 50%; background: #34d399; margin-right: .6rem;
  box-shadow: 0 0 0 0 rgba(52,211,153,.7); animation: pulse 1.6s infinite; }
@keyframes pulse { 70% { box-shadow: 0 0 0 .55rem rgba(52,211,153,0); } 100% { box-shadow: 0 0 0 0 rgba(52,211,153,0); } }

/* template cards */
[class*="st-key-tplcard"] { background: linear-gradient(160deg, var(--card-1), var(--card-2)); border: 1px solid var(--border);
  border-radius: 16px; padding: 1rem 1rem .9rem; min-height: 11rem; transition: all .15s ease; }
[class*="st-key-tplcard"] > div:last-child { margin-top: auto; }
[class*="st-key-tplcard"]:hover { border-color: rgba(139,92,246,.6); transform: translateY(-2px); }
[class*="st-key-tplcard_sel"] { border-color: rgba(139,92,246,.9);
  box-shadow: 0 0 0 1px rgba(139,92,246,.5), 0 8px 30px rgba(99,102,241,.28); }
.tpl-name { font-weight: 700; color: var(--accent-title); font-size: 1rem; }
.tpl-desc { color: var(--text-soft); font-size: .86rem; line-height: 1.4; }
.chips { margin-top: .6rem; }
.chip { display: inline-block; margin: 0 .3rem .3rem 0; padding: .1rem .5rem; border-radius: 7px; font-size: .74rem;
  color: var(--text-soft); background: var(--code-bg); font-family: ui-monospace, SFMono-Regular, Menlo, monospace; }

/* type picker dialog */
section[role="dialog"] { background: var(--dialog-bg) !important; border: 1px solid var(--border-strong);
  border-radius: 18px; }
section[role="dialog"] h2 { position: absolute; width: 1px !important; height: 1px !important; overflow: hidden;
  clip: rect(0 0 0 0); opacity: 0; }
.dlg-title { font-size: 1.3rem; font-weight: 700; color: var(--text-strong); margin: 0 2.5rem .9rem 0; }
.dlg-field { color: var(--field-color); }
/* the title block spans the dialog width and would otherwise swallow clicks meant for the close button */
div[data-testid="stElementContainer"]:has(.dlg-title) { pointer-events: none; }
section[role="dialog"] button[aria-label="Close"] { z-index: 10; }
section[role="dialog"] div[data-testid="stVerticalBlock"], section[role="dialog"] div[data-testid="stHorizontalBlock"] {
  gap: .2rem !important; }
[class*="st-key-dlg_group_"] { border-bottom: 1px solid var(--border-soft); padding: .9rem 0 .35rem; margin-bottom: .4rem; }
[class*="st-key-dlg_group_"] p { color: var(--text-dim); font-size: .75rem; letter-spacing: .1em; text-transform: uppercase;
  font-weight: 700; display: flex; align-items: center; gap: .4rem; }
[class*="st-key-pick_list_"] { padding-right: .6rem; max-height: 72vh !important; }
[class*="st-key-pick_list_"]::-webkit-scrollbar { width: 8px; }
[class*="st-key-pick_list_"]::-webkit-scrollbar-thumb { background: var(--scroll-thumb); border-radius: 8px; }
[class*="st-key-pick_list_"]::-webkit-scrollbar-track { background: var(--scroll-track); border-radius: 8px; }
[class*="st-key-pick_"] button { min-height: 2rem !important; height: 2rem; padding: 0 .7rem; justify-content: flex-start;
  border-color: transparent; background: transparent; }
[class*="st-key-pick_"] button div, [class*="st-key-pick_"] button p { text-align: left; justify-content: flex-start; }
[class*="st-key-pick_"] button:hover { background: var(--surface-hover); border-color: var(--border); }
[class*="st-key-pick_"] button[kind="primary"] { background: rgba(139,92,246,.22); border: 1px solid rgba(139,92,246,.7);
  box-shadow: none; color: var(--text-strong); }

/* docs */
.doc-table { width: 100%; border-collapse: collapse; margin: .4rem 0 .4rem; font-size: .88rem; background: var(--tile);
  border-radius: 12px; overflow: hidden; }
.doc-table th { text-align: left; color: var(--text-dim); font-size: .72rem; text-transform: uppercase; letter-spacing: .08em;
  padding: .6rem .8rem; border-bottom: 1px solid var(--border-strong); }
.doc-table td { padding: .65rem .8rem; vertical-align: top; border-bottom: 1px solid var(--border-soft); color: var(--text); }
.doc-table code, [data-testid="stMarkdownContainer"] code { background: var(--code-bg); padding: .05rem .35rem;
  border-radius: 5px; color: var(--text-code); }
[data-testid="stMarkdownContainer"] table { background: var(--tile); border-radius: 12px; overflow: hidden; }
[data-testid="stMarkdownContainer"] table, [data-testid="stMarkdownContainer"] th, [data-testid="stMarkdownContainer"] td {
  border-color: var(--border) !important; }
[class*="st-key-card_doc_toc"] { position: sticky; top: 4.5rem; }
[class*="st-key-card_docs_"] h2 { font-size: 1.5rem; }
[class*="st-key-card_docs_"] h3 { font-size: 1.1rem; margin-top: .6rem; }
[class*="st-key-docs_link"] a, [class*="st-key-docs_link"] p { color: var(--text-dim) !important; }
[class*="st-key-docs_link"] a:hover p { color: var(--text-strong) !important; }
"""
