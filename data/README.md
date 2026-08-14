# Data Directory

> Note: With MinIO mounted from Phase 1 (per user request),
> this directory is reserved only for **local-only artifacts**:
> - CSV fixtures used by tests
> - One-off notebooks (if any)
>
> Production data lives in MinIO buckets:
> - `weather-raw/` — unmodified BMKG payloads
> - `weather-staged/` — parsed/normalized Parquet
> - `weather-marts/` — dbt marts (consumed by BI)

## Local-only subfolders
- `raw/` — gitignored, for ad-hoc local dumps during dev
- `staged/` — gitignored
