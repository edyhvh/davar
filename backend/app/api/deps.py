"""
API dependencies for route handlers
"""

from app.security import require_api_key

# Export common dependencies for use in routes
__all__ = ["require_api_key"]