"""Utilities for syncing private TS2009 files from Supabase Storage."""

from __future__ import annotations

from dataclasses import dataclass
import json
import logging
from pathlib import Path
from typing import Any

from app.config import settings

try:
    from supabase import create_client
except ImportError:  # pragma: no cover - handled at runtime in callers
    create_client = None

try:
    import httpx
except ImportError:  # pragma: no cover - optional at import time
    httpx = None


TS2009_BUCKET = "ts2009"
MANIFEST_FILE_NAME = ".sync_manifest.json"


def _raise_network_error(exc: Exception) -> None:
    raise RuntimeError(
        "TS2009 sync could not reach Supabase Storage. "
        "If you are behind a proxy, verify HTTPS_PROXY/HTTP_PROXY and NO_PROXY settings. "
        "You can disable startup sync with DAVAR_TS2009_SYNC_ON_STARTUP=false and run "
        "scripts/sync_ts2009.py manually when network access is available. "
        f"Original error: {exc}"
    ) from exc


@dataclass
class Ts2009SyncResult:
    """Result object for TS2009 sync operations."""

    listed: int
    downloaded: int
    skipped: int
    manifest_path: str


def _build_remote_signature(file_info: dict[str, Any]) -> dict[str, Any]:
    metadata = file_info.get("metadata") or {}
    return {
        "updated_at": file_info.get("updated_at"),
        "last_accessed_at": file_info.get("last_accessed_at"),
        "size": metadata.get("size") or file_info.get("size"),
        "etag": metadata.get("eTag") or metadata.get("etag"),
    }


def _load_manifest(manifest_path: Path) -> dict[str, dict[str, Any]]:
    if not manifest_path.exists():
        return {}

    try:
        raw = json.loads(manifest_path.read_text(encoding="utf-8"))
        files = raw.get("files")
        if isinstance(files, dict):
            return {str(name): dict(meta) for name, meta in files.items()}
    except Exception:
        return {}

    return {}


def _write_manifest(manifest_path: Path, files: dict[str, dict[str, Any]]) -> None:
    payload = {
        "bucket": TS2009_BUCKET,
        "files": files,
    }
    manifest_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def sync_ts2009_files(logger: logging.Logger | None = None) -> Ts2009SyncResult:
    """Sync TS2009 JSON files with incremental skip for unchanged files."""
    log = logger or logging.getLogger(__name__)

    if create_client is None:
        raise RuntimeError("supabase package not installed")

    supabase_url = settings.supabase_url
    supabase_key = settings.supabase_service_key
    if not supabase_url or not supabase_key:
        raise RuntimeError(
            "supabase_url and supabase_service_key must be configured "
            "(via DAVAR_SUPABASE_URL and DAVAR_SUPABASE_SERVICE_KEY)"
        )

    data_path = Path(settings.data_path) / "ts2009"
    data_path.mkdir(parents=True, exist_ok=True)

    manifest_path = data_path / MANIFEST_FILE_NAME
    existing_manifest = _load_manifest(manifest_path)
    next_manifest: dict[str, dict[str, Any]] = {}

    supabase = create_client(supabase_url, supabase_key)
    bucket = supabase.storage.from_(TS2009_BUCKET)
    try:
        files = bucket.list()
    except Exception as exc:
        if httpx is not None and isinstance(exc, (httpx.ProxyError, httpx.TransportError)):
            _raise_network_error(exc)
        if "ProxyError" in type(exc).__name__ or "Bad Gateway" in str(exc):
            _raise_network_error(exc)
        raise

    downloaded = 0
    skipped = 0
    json_files = [f for f in files if str(f.get("name", "")).endswith(".json")]

    for file_info in sorted(json_files, key=lambda item: str(item.get("name", ""))):
        name = str(file_info.get("name", "")).strip()
        if not name:
            continue

        remote_signature = _build_remote_signature(file_info)
        next_manifest[name] = remote_signature
        local_file_path = data_path / name
        previous_signature = existing_manifest.get(name)

        if local_file_path.exists() and previous_signature == remote_signature:
            skipped += 1
            continue

        log.info("Downloading TS2009 file: %s", name)
        try:
            content = bucket.download(name)
        except Exception as exc:
            if httpx is not None and isinstance(exc, (httpx.ProxyError, httpx.TransportError)):
                _raise_network_error(exc)
            if "ProxyError" in type(exc).__name__ or "Bad Gateway" in str(exc):
                _raise_network_error(exc)
            raise
        local_file_path.write_bytes(content)
        downloaded += 1

    _write_manifest(manifest_path, next_manifest)
    return Ts2009SyncResult(
        listed=len(json_files),
        downloaded=downloaded,
        skipped=skipped,
        manifest_path=str(manifest_path),
    )
