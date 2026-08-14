"""
BMKG Ingestion Package
=======================

Fetches weather forecast data from data.bmkg.go.id, parses the
XML/JSON payloads, and uploads raw payloads to MinIO for downstream
processing.

Phase 1 scope:
    - Fetch all province-level forecast endpoints
    - Parse XML payloads
    - Upload raw XML + normalized JSON to MinIO
    - Structured logging to stdout

Submodules (added progressively):
    - parser:    XML → dict / Pydantic models
    - client:    HTTP client with retries
    - uploader:  MinIO upload helper
    - cli:       `python -m bmkg` entrypoint
"""

__version__ = "0.1.0"
