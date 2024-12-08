-- Connect to source database and create publication for all tables
DROP PUBLICATION IF EXISTS dbz_publication;

-- For PostgreSQL 10 and above
-- CREATE PUBLICATION dbz_publication FOR ALL TABLES;

-- For specific schema (PostgreSQL 15 and above)
-- CREATE PUBLICATION dbz_publication FOR TABLES IN SCHEMA public;

-- Or for specific tables
CREATE PUBLICATION dbz_publication 
FOR TABLE public.dim_artist, public.dim_album, public.dim_song, public.fact_history;

-- Set default replication identity to FULL for all tables
DO $$
DECLARE
    r RECORD;
BEGIN
    FOR r IN SELECT schemaname, tablename 
             FROM pg_tables 
             WHERE schemaname = 'public'
    LOOP
        EXECUTE format(
            'ALTER TABLE %I.%I REPLICA IDENTITY FULL',
            r.schemaname,
            r.tablename
        );
    END LOOP;
END $$;