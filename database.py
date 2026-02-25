# Re-export for local runs and tests (app uses api.database on Vercel)
from api.database import db

__all__ = ["db"]
