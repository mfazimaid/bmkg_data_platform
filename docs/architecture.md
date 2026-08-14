# Architecture Decision Records (ADRs)

Mirror of `CLAUDE.md` §2 with explicit decisions per phase.

---

## ADR-001: Monorepo

**Status**: ✅ Accepted (Phase 0)
**Context**: Repo structure for multi-fase lakehouse build.
**Decision**: Single monorepo.
**Consequences**:
- (+) Easy cross-phase refactors (e.g. schema in ingestion → dbt)
- (+) Single CI pipeline (cheap at our scale)
- (-) Larger repo over time; mitigated by `.dockerignore` + per-phase Dockerfiles

---

## ADR-002: pip + venv (no Poetry, no uv)

**Status**: ✅ Accepted (Phase 0)
**Context**: Python toolchain for host dev environment.
**Decision**: Standard `pip` + `venv` (stdlib only).
**Consequences**:
- (+) Zero extra tooling; stdlib battle-tested
- (+) Predictable resolution semantics
- (-) Slower installs than `uv`; acceptable for our scale

---

## ADR-003: Docker Compose profiles (not multiple files)

**Status**: ✅ Accepted (Phase 0)
**Context**: Incremental service rollout across 14 phases.
**Decision**: Single `docker-compose.yml` with named profiles.
**Consequences**:
- (+) Single source of truth
- (+) `docker compose --profile phase-N up` is intuitive
- (-) Long compose file; mitigated by section comments

---

## ADR-004: MinIO from Phase 1 (no host staging)

**Status**: ✅ Accepted (Phase 0)
**Context**: Where should raw BMKG payloads land in Phase 1?
**Decision**: Mount MinIO from Phase 1; skip host `data/raw/` staging.
**Consequences**:
- (+) Production-like behavior from Day 1
- (+) No manual file shuffling when Phase 2 (Lake) begins
- (-) MinIO is now a hard dependency for `make phase-1-up`
- (-) Slight Docker overhead vs. local FS (negligible at MB/day)

---

## Architecture diagram

See `CLAUDE.md` §2. This document will track ADRs only.
