# Vercel serverless entry: run from api/ so bundle includes this package.
import os
import sys

# Project root (parent of api/) must be on path for "from api.main import app"
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

try:
    from api.main import app
except Exception as e:
    import traceback
    from fastapi import FastAPI
    from fastapi.responses import PlainTextResponse
    app = FastAPI()

    @app.get("/")
    @app.get("/health")
    @app.get("/{rest:path}")
    def _err(rest: str = ""):
        return PlainTextResponse(
            f"Error: {type(e).__name__}: {e}\n\n{traceback.format_exc()}",
            status_code=500,
        )
