import sys
from pathlib import Path

# Ensure root directory is in sys.path for serverless execution
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.main import app  # noqa: E402

# Export app for Vercel WSGI/ASGI handler
__all__ = ["app"]
