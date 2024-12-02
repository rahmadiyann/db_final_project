-- Connect to source database and create publication for all tables
DROP PUBLICATION IF EXISTS dbz_publication;

-- Create publication for all existing tables
CREATE PUBLICATION dbz_publication FOR ALL TABLES;

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