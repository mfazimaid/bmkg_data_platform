# BMKG Ingestion (Phase 1)

**Status**: 🟡 Scaffolded (Phase 0)

**Will be implemented in Phase 1**:
- `client.py` — HTTP client with retry/backoff via `tenacity`
- `parser.py` — XML → Pydantic models
- `uploader.py` — MinIO S3 client (raw bucket)
- `cli.py` — `python -m bmkg fetch`
- `tests/` — unit tests for parser (with fixture XML)

**Data source**: https://data.bmkg.go.id/prakiraan-cuaca/
