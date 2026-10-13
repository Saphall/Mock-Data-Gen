"""Command line entry point: `mock-data-gen` (UI + API) or `mock-data-gen api` (API only)."""

import subprocess
import sys
from pathlib import Path

from .config import API_HOST, API_PORT


def main() -> None:
    if sys.argv[1:2] == ["api"]:
        import uvicorn

        from .api import app

        uvicorn.run(app, host=API_HOST, port=API_PORT)
        return
    app_path = Path(__file__).parent / "ui" / "app.py"
    cmd = [sys.executable, "-m", "streamlit", "run", str(app_path), "--theme.base=dark",
           "--theme.primaryColor=#8b5cf6", "--theme.backgroundColor=#151c38",
           "--theme.secondaryBackgroundColor=#1e2748", "--browser.gatherUsageStats=false",
           "--client.toolbarMode=minimal",
           *sys.argv[1:]]
    raise SystemExit(subprocess.call(cmd))
