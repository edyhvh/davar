"""Supabase client setup (future user data support)."""

from typing import Optional
from importlib import import_module

try:
    _supabase_module = import_module("supabase")
    create_client = getattr(_supabase_module, "create_client")
    Client = getattr(_supabase_module, "Client")
except Exception:  # pragma: no cover
    Client = None
    create_client = None

from app.config import settings


def get_supabase_client() -> Optional["Client"]:
    """Create a Supabase client if credentials are configured."""
    if not settings.supabase_url or not settings.supabase_key:
        return None
    if create_client is None:
        return None
    return create_client(settings.supabase_url, settings.supabase_key)
