"""Runtime settings, overridable through environment variables."""

import os

API_HOST = os.environ.get("MOCK_DATA_API_HOST", "127.0.0.1")
API_PORT = int(os.environ.get("MOCK_DATA_API_PORT", "8000"))
# URL shown to users; differs from the bind address when running in a container.
API_PUBLIC_URL = os.environ.get("MOCK_DATA_API_PUBLIC_URL", f"http://localhost:{API_PORT}")
OUTPUT_DIR = os.environ.get("MOCK_DATA_OUTPUT_DIR", "output")
