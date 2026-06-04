from app.core.settings import get_settings
from app.db.sqlite import SQLiteStore


def get_store() -> SQLiteStore:
    return SQLiteStore(get_settings().database_path)
