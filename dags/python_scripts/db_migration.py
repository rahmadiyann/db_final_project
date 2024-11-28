import psycopg2
from psycopg2.extras import DictCursor
import logging
from typing import Dict, List, Tuple
import sys
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'migration_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)

class PostgresMigrator:
    def __init__(self, source_params: Dict, target_params: Dict, specific_tables: List[str] = None):
        self.source_params = source_params
        self.target_params = target_params
        self.source_conn = None
        self.target_conn = None
        self.specific_tables = specific_tables

    def connect(self):
        """Establish connections to source and target databases"""
        try:
            self.source_conn = psycopg2.connect(**self.source_params)
            self.target_conn = psycopg2.connect(**self.target_params)
            logging.info("Successfully connected to both databases")
        except Exception as e:
            logging.error(f"Connection error: {str(e)}")
            sys.exit(1)

    def close_connections(self):
        """Close database connections"""
        if self.source_conn:
            self.source_conn.close()
        if self.target_conn:
            self.target_conn.close()
        logging.info("Connections closed")

    def get_tables(self) -> List[str]:
        """Get list of tables from source database"""
        query = """
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
        """
        with self.source_conn.cursor() as cur:
            cur.execute(query)
            all_tables = [table[0] for table in cur.fetchall()]
            
            # If specific tables are specified, validate they exist
            if self.specific_tables:
                invalid_tables = [t for t in self.specific_tables if t not in all_tables]
                if invalid_tables:
                    raise ValueError(f"Tables not found in source database: {invalid_tables}")
                return self.specific_tables
            return all_tables

    def get_target_tables(self) -> List[str]:
        """Get list of tables from target database"""
        query = """
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
        """
        with self.target_conn.cursor() as cur:
            cur.execute(query)
            return [table[0] for table in cur.fetchall()]

    def get_partitioned_tables(self) -> Dict[str, List[str]]:
        """Get partitioned tables and their partitions"""
        query = """
            SELECT parent.relname AS parent_table,
                   child.relname AS partition
            FROM pg_inherits
            JOIN pg_class parent ON pg_inherits.inhparent = parent.oid
            JOIN pg_class child ON pg_inherits.inhrelid = child.oid
            JOIN pg_namespace n ON n.oid = parent.relnamespace
            WHERE n.nspname = 'public'
        """
        partitions = {}
        with self.source_conn.cursor() as cur:
            cur.execute(query)
            for parent, child in cur.fetchall():
                if parent not in partitions:
                    partitions[parent] = []
                partitions[parent].append(child)
        return partitions

    def get_table_schema(self, table_name: str) -> str:
        """Get CREATE TABLE statement for a given table"""
        query = """
            SELECT 
                'CREATE TABLE ' || %s || ' (' ||
                string_agg(
                    column_name || ' ' || 
                    data_type || 
                    CASE 
                        WHEN character_maximum_length IS NOT NULL 
                        THEN '(' || character_maximum_length || ')'
                        ELSE ''
                    END ||
                    CASE 
                        WHEN is_nullable = 'NO' THEN ' NOT NULL'
                        ELSE ''
                    END ||
                    CASE 
                        WHEN column_default IS NOT NULL 
                        THEN ' DEFAULT ' || column_default
                        ELSE ''
                    END,
                    ', '
                ) ||
                CASE 
                    WHEN (
                        SELECT COUNT(*) 
                        FROM information_schema.table_constraints tc
                        WHERE tc.table_name = c.table_name 
                        AND tc.constraint_type = 'PRIMARY KEY'
                    ) > 0 
                    THEN ', ' || (
                        SELECT 'PRIMARY KEY (' || string_agg(ccu.column_name, ', ') || ')'
                        FROM information_schema.table_constraints tc
                        JOIN information_schema.constraint_column_usage ccu 
                            ON tc.constraint_name = ccu.constraint_name
                        WHERE tc.table_name = c.table_name 
                        AND tc.constraint_type = 'PRIMARY KEY'
                    )
                    ELSE ''
                END ||
                CASE 
                    WHEN (
                        SELECT COUNT(*) 
                        FROM information_schema.table_constraints tc
                        WHERE tc.table_name = c.table_name 
                        AND tc.constraint_type = 'FOREIGN KEY'
                    ) > 0 
                    THEN ', ' || (
                        SELECT string_agg(
                            'FOREIGN KEY (' || kcu.column_name || 
                            ') REFERENCES ' || ccu.table_name || 
                            '(' || ccu.column_name || ')',
                            ', '
                        )
                        FROM information_schema.table_constraints tc
                        JOIN information_schema.key_column_usage kcu 
                            ON tc.constraint_name = kcu.constraint_name
                        JOIN information_schema.constraint_column_usage ccu 
                            ON tc.constraint_name = ccu.constraint_name
                        WHERE tc.table_name = c.table_name 
                        AND tc.constraint_type = 'FOREIGN KEY'
                    )
                    ELSE ''
                END ||
                ');'
            FROM information_schema.columns c
            WHERE table_name = %s
            GROUP BY table_name;
        """
        with self.source_conn.cursor() as cur:
            cur.execute(query, (table_name, table_name))
            return cur.fetchone()[0]

    def get_indexes(self, table_name: str) -> List[str]:
        """Get CREATE INDEX statements for a given table"""
        query = """
            SELECT indexdef 
            FROM pg_indexes 
            WHERE tablename = %s 
            AND schemaname = 'public'
        """
        with self.source_conn.cursor() as cur:
            cur.execute(query, (table_name,))
            return [idx[0] for idx in cur.fetchall()]

    def get_partition_info(self, table_name: str) -> str:
        """Get partition information for a table"""
        partition_query = """
            SELECT pg_get_partkeydef(%s::regclass) AS partition_key;
        """
        with self.source_conn.cursor() as cur:
            cur.execute(partition_query, (table_name,))
            partition_key = cur.fetchone()[0]
            return partition_key

    def table_exists(self, table_name: str) -> bool:
        """Check if table exists in target database"""
        query = """
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = %s
            );
        """
        with self.target_conn.cursor() as cur:
            cur.execute(query, (table_name,))
            return cur.fetchone()[0]

    def get_dependencies(self) -> Dict[str, List[str]]:
        """Get table dependencies based on foreign keys"""
        query = """
            SELECT
                tc.table_name,
                ccu.table_name AS foreign_table_name
            FROM information_schema.table_constraints AS tc
            JOIN information_schema.constraint_column_usage AS ccu
            ON ccu.constraint_name = tc.constraint_name
            WHERE tc.constraint_type = 'FOREIGN KEY'
            AND tc.table_schema = 'public'
        """
        dependencies = {}
        with self.source_conn.cursor() as cur:
            cur.execute(query)
            for table, foreign_table in cur.fetchall():
                if foreign_table not in dependencies:
                    dependencies[foreign_table] = []
                dependencies[foreign_table].append(table)
        return dependencies

    def get_migration_order(self) -> List[str]:
        """Determine correct order of table migration based on dependencies and table types"""
        tables = self.get_tables()
        dependencies = self.get_dependencies()
        migration_order = []
        visited = set()

        def visit(table):
            if table in visited:
                return
            visited.add(table)
            # Get tables that this table depends on (foreign key references)
            for dep_table, dependent_tables in dependencies.items():
                if table in dependent_tables and dep_table in tables:
                    visit(dep_table)
            migration_order.append(table)

        # Separate tables into dimensions and facts
        dim_tables = [table for table in tables if table.startswith('dim_')]
        fact_tables = [table for table in tables if table.startswith('fact_')]
        other_tables = [table for table in tables if not table.startswith(('dim_', 'fact_'))]

        # Process tables in order: dimensions -> others -> facts
        for table in dim_tables:
            if table not in visited:
                visit(table)
            
        for table in other_tables:
            if table not in visited:
                visit(table)
            
        for table in fact_tables:
            if table not in visited:
                visit(table)

        return migration_order

    def migrate_table(self, table_name: str, batch_size: int = 10000):
        """Migrate data for a single table"""
        try:
            # Get total count
            with self.source_conn.cursor() as cur:
                cur.execute(f"SELECT COUNT(*) FROM {table_name}")
                total_rows = cur.fetchone()[0]

            # Copy data in batches
            with self.source_conn.cursor(name='fetch_data') as source_cur, \
                 self.target_conn.cursor() as target_cur:
                
                source_cur.itersize = batch_size
                source_cur.execute(f"SELECT * FROM {table_name}")
                
                copied_rows = 0
                while True:
                    records = source_cur.fetchmany(batch_size)
                    if not records:
                        break
                    
                    # Prepare the INSERT statement
                    columns = [desc[0] for desc in source_cur.description]
                    placeholders = ','.join(['%s'] * len(columns))
                    insert_query = f"INSERT INTO {table_name} ({','.join(columns)}) VALUES ({placeholders})"
                    
                    target_cur.executemany(insert_query, records)
                    self.target_conn.commit()
                    
                    copied_rows += len(records)
                    logging.info(f"Migrated {copied_rows}/{total_rows} rows for table {table_name}")

        except Exception as e:
            logging.error(f"Error migrating table {table_name}: {str(e)}")
            self.target_conn.rollback()
            raise

    def get_sequences(self, table_name: str) -> List[Dict]:
        """Get sequence information for columns in a table"""
        query = """
            SELECT 
                pg_get_serial_sequence('public.' || quote_ident(%s), a.attname) as sequence_name,
                a.attname as column_name
            FROM pg_attribute a
            JOIN pg_class c ON a.attrelid = c.oid
            WHERE c.relname = %s
            AND a.attnum > 0
            AND NOT a.attisdropped
            AND pg_get_serial_sequence('public.' || quote_ident(%s), a.attname) IS NOT NULL;
        """
        sequences = []
        with self.source_conn.cursor() as cur:
            cur.execute(query, (table_name, table_name, table_name))
            for sequence_name, column_name in cur.fetchall():
                # Get the sequence details
                seq_query = f"""
                    SELECT 
                        sequence_name,
                        data_type,
                        start_value,
                        minimum_value,
                        maximum_value,
                        increment
                    FROM information_schema.sequences
                    WHERE sequence_schema = 'public'
                    AND sequence_name = %s;
                """
                cur.execute(seq_query, (sequence_name.split('.')[-1],))
                seq_details = cur.fetchone()
                if seq_details:
                    sequences.append({
                        'sequence_name': seq_details[0],
                        'data_type': seq_details[1],
                        'start_value': seq_details[2],
                        'minimum_value': seq_details[3],
                        'maximum_value': seq_details[4],
                        'increment': seq_details[5],
                        'column_name': column_name
                    })
        return sequences

    def create_table(self, table_name: str):
        """Create table and its sequences in target database"""
        try:
            # First create any sequences needed by the table
            sequences = self.get_sequences(table_name)
            for seq in sequences:
                seq_name = seq['sequence_name']
                create_seq_sql = f"""
                    CREATE SEQUENCE IF NOT EXISTS {seq_name}
                    INCREMENT {seq['increment']}
                    MINVALUE {seq['minimum_value']}
                    MAXVALUE {seq['maximum_value']}
                    START {seq['start_value']};
                """
                with self.target_conn.cursor() as cur:
                    cur.execute(create_seq_sql)
                    logging.info(f"Created sequence {seq_name}")

            # Then create the table
            schema = self.get_table_schema(table_name)
            with self.target_conn.cursor() as cur:
                cur.execute(schema)
                
                # Set sequence ownership
                for seq in sequences:
                    seq_name = seq['sequence_name']
                    col_name = seq['column_name']
                    alter_seq_sql = f"""
                        ALTER SEQUENCE {seq_name} OWNED BY {table_name}.{col_name};
                    """
                    cur.execute(alter_seq_sql)
                    
            self.target_conn.commit()
            logging.info(f"Created table {table_name}")
            
        except Exception as e:
            logging.error(f"Error creating table {table_name}: {str(e)}")
            self.target_conn.rollback()
            raise

    def migrate_database(self):
        """Perform the complete database migration"""
        try:
            self.connect()
            
            # Get tables in correct migration order
            tables = self.get_migration_order()
            target_tables = self.get_target_tables()
            partitioned_tables = self.get_partitioned_tables()
            
            # Create missing tables and migrate data
            for table in tables:
                if not self.table_exists(table):
                    logging.info(f"Table {table} does not exist in target database. Creating...")
                    self.create_table(table)
                
                logging.info(f"Migrating data for table {table}")
                self.migrate_table(table)
            
            # Create indexes
            for table in tables:
                indexes = self.get_indexes(table)
                for idx in indexes:
                    try:
                        logging.info(f"Creating index on {table}")
                        with self.target_conn.cursor() as cur:
                            cur.execute(idx)
                        self.target_conn.commit()
                    except psycopg2.errors.DuplicateTable:
                        logging.info(f"Index already exists on {table}")
                        self.target_conn.rollback()
                        continue
            
            logging.info("Migration completed successfully")
            
        except Exception as e:
            logging.error(f"Migration failed: {str(e)}")
            raise
        finally:
            self.close_connections()
            
def migrate_db(source_params, target_params, specific_tables=None):
    """
    Migrate database tables from source to target
    
    Args:
        source_params (dict): Source database connection parameters
        target_params (dict): Target database connection parameters
        specific_tables (list): Optional list(string) of specific table names to migrate. 
                              If None, all tables will be migrated.
    """
    
    ## Uncomment to use this file as a standalone script
    
    # Database connection parameters
    # source_params = {
    #     'dbname': 'verceldb',
    #     'user': 'default',
    #     'password': 'AVb2Io9pqyWm',
    #     'host': 'ep-super-shape-a12kklqk.ap-southeast-1.aws.neon.tech',
    #     'port': '5432'
    # }
    
    # target_params = {
    #     'dbname': 'local',
    #     'user': 'postgres',
    #     'password': 'postgres',
    #     'host': 'localhost',
    #     'port': '5432'
    # }
    
    migrator = PostgresMigrator(source_params, target_params, specific_tables)
    migrator.migrate_database()

# if __name__ == "__main__":
#     migrate_db()