"""Runtime settings, overridable through environment variables."""

import os
from pathlib import Path


def _api_enabled() -> bool:
    flag = os.environ.get("MOCK_DATA_API_ENABLED")
    if flag is not None:
        return flag.strip().lower() in ("1", "true", "yes", "on")
    # Streamlit Community Cloud mounts the repo here and exposes only the Streamlit port.
    return not Path("/mount/src").exists()


API_ENABLED = _api_enabled()
API_HOST = os.environ.get("MOCK_DATA_API_HOST", "127.0.0.1")
API_PORT = int(os.environ.get("MOCK_DATA_API_PORT", "8000"))
# URL shown to users; differs from the bind address when running in a container.
API_PUBLIC_URL = os.environ.get("MOCK_DATA_API_PUBLIC_URL", f"http://localhost:{API_PORT}")
OUTPUT_DIR = os.environ.get("MOCK_DATA_OUTPUT_DIR", "output")
