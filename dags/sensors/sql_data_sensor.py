from airflow.sensors.base import BaseSensorOperator
from airflow.utils.decorators import apply_defaults
from airflow.providers.postgres.hooks.postgres import PostgresHook
from datetime import datetime, timedelta
from typing import Optional

class LastMonthDataSensor(BaseSensorOperator):
    """
    Sensor to check if dimension tables and fact_history have data from last 31 days.
    For fact_history, checks both added_at and played_at columns.
    For dimension tables, checks added_at column.
    """
    
    @apply_defaults
    def __init__(
        self,
        postgres_conn_id: str = "main_postgres",
        database: str = "postgres_db",
        *args,
        **kwargs
    ) -> None:
        super().__init__(*args, **kwargs)
        self.postgres_conn_id = postgres_conn_id
        self.database = database

    def poke(self, context: dict) -> bool:
        hook = PostgresHook(postgres_conn_id=self.postgres_conn_id)
        
        # Calculate date range for last 31 days
        end_date = datetime.now()
        start_date = end_date - timedelta(days=31)
        
        # SQL query to check data existence
        check_query = """
        WITH dimension_checks AS (
            -- Check dim_album
            SELECT 
                CASE 
                    WHEN COUNT(*) > 0 THEN true 
                    ELSE false 
                END as has_data,
                'dim_album' as table_name,
                COUNT(*) as record_count
            FROM public.dim_album
            WHERE added_at >= %s AND added_at <= %s
            
            UNION ALL
            
            -- Check dim_artist
            SELECT 
                CASE 
                    WHEN COUNT(*) > 0 THEN true 
                    ELSE false 
                END as has_data,
                'dim_artist' as table_name,
                COUNT(*) as record_count
            FROM public.dim_artist
            WHERE added_at >= %s AND added_at <= %s
            
            UNION ALL
            
            -- Check dim_song
            SELECT 
                CASE 
                    WHEN COUNT(*) > 0 THEN true 
                    ELSE false 
                END as has_data,
                'dim_song' as table_name,
                COUNT(*) as record_count
            FROM public.dim_song
            WHERE added_at >= %s AND added_at <= %s
            
            UNION ALL
            
            -- Check fact_history added_at
            SELECT 
                CASE 
                    WHEN COUNT(*) > 0 THEN true 
                    ELSE false 
                END as has_data,
                'fact_history (added_at)' as table_name,
                COUNT(*) as record_count
            FROM public.fact_history
            WHERE added_at >= %s AND added_at <= %s
            
            UNION ALL
            
            -- Check fact_history played_at
            SELECT 
                CASE 
                    WHEN COUNT(*) > 0 THEN true 
                    ELSE false 
                END as has_data,
                'fact_history (played_at)' as table_name,
                COUNT(*) as record_count
            FROM public.fact_history
            WHERE played_at >= %s AND played_at <= %s
        )
        SELECT 
            bool_and(has_data) as all_tables_have_data,
            json_agg(json_build_object(
                'table', table_name,
                'has_data', has_data,
                'count', record_count
            )) as table_status
        FROM dimension_checks;
        """
        
        params = [
            start_date, end_date,  # for dim_album
            start_date, end_date,  # for dim_artist
            start_date, end_date,  # for dim_song
            start_date, end_date,  # for fact_history added_at
            start_date, end_date,  # for fact_history played_at
        ]
        
        result = hook.get_first(check_query, parameters=params)
        all_tables_have_data, table_status = result
        
        # Log detailed status for each table
        self.log.info(f"Data check for last 31 days ({start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}):")
        for status in table_status:
            self.log.info(
                f"Table: {status['table']}, "
                f"Has Data: {status['has_data']}, "
                f"Record Count: {status['count']}"
            )
            
        if not all_tables_have_data:
            self.log.warning(
                f"Missing data for last 31 days ({start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}). "
                "Check the logs above for specific tables."
            )
        else:
            self.log.info(
                f"All required data found for last 31 days ({start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')})"
            )
            
        return all_tables_have_data 