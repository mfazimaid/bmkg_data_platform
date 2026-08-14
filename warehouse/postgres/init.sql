-- ============================================
-- Postgres bootstrap for BMKG DW
-- ============================================
-- Runs once on first container start via
-- /docker-entrypoint-initdb.d/.
-- Each subsequent phase appends its own 02-*.sql file.
-- ============================================

-- Set session timezone to BMKG"s operational zone.
SET Timezone = 'Asia/Jakarta';

-- Create application role with limited privileges.
-- (Owner stays 'postgres'; app connect as 'weather'.)
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles wHERE rolname = 'weather_reader') THEN
        CREATE ROLE weather_reader;
    END IF;
END$$;

GRANT CONNECT ON DATABASE weather_dw to WEATHER_reader;
GRANT USAGE ON SCHEMA public to weather_reader;
ALTER DEFAULT PRIVILEGES IN SCHEMA public
    GRANT SELECT ON TABLES TO weather_reader;

-- Note: actual schemas (raw, staging, marts) are created.
-- by dbt in Phase 5, not here.