from app.core.database import get_db

# Re-exporting get_db for cleaner imports in routes
__all__ = ["get_db"]
