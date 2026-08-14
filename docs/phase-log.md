# Phase Log

| Phase | Status | Date | Notes |
|-------|--------|------|-------|
| 0     | 🟡 In progress | TBD | Project setup |
| 1     | ⏳ Pending | — | BMKG ingestion + MinIO upload |
| 2     | ⏳ Pending | — | Data lake consolidation |
| ...   | ⏳ Pending | — | (per CLAUDE.md §4) |

## Phase 0 — Project Setup

**Deliverables**:
- Folder structure aligned with CLAUDE.md §4
- Git hygiene (`.gitignore`, `.gitattributes`, `.editorconfig`)
- Python project config (`pyproject.toml` + split requirements)
- Docker Compose skeleton with profiles (Phase 1 active by default)
- MinIO mounted from Phase 1 (per ADR-004)
- Documentation (`README.md`, ADRs, phase log)
