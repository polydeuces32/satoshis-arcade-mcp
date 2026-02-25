# Vercel entrypoint
import os
import sys
_ROOT = os.path.dirname(os.path.abspath(__file__))
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
            f"Startup error:\n{type(e).__name__}: {e}\n\n{traceback.format_exc()}",
            status_code=500,
        )
