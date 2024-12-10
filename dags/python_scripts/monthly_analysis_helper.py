import json
from datetime import datetime

def prepare_soda_check(table: str):
    month_year = datetime.now().strftime("%Y%m")
    with open(f'/data/spotify_analysis/xcom/{table}_{month_year}.json', 'r') as file:
        data = json.load(file)
        
    return data

def soda_check(table: str):
    """
    Create dynamic Soda check variables from xcom metrics
    Only create checks for numeric columns (int, bigint, float, double)
    """
    data = prepare_soda_check(table)
    soda_variables = {}
    
    # Get row count from any column (they should all be the same)
    soda_variables['row_count'] = data[0]['row_count']
    
    # Create variables for each column's metrics
    for column_metric in data:
        column_name = column_metric['column_name']
        
        # Skip id column as it's handled by generic checks
        if column_name == 'id':
            continue
            
        # Only process metrics if all values are present (numeric columns)
        if all(column_metric[key] is not None for key in ['min_value', 'max_value', 'average']):
            soda_variables[f'{column_name}_min'] = float(column_metric['min_value'])
            soda_variables[f'{column_name}_max'] = float(column_metric['max_value'])
            soda_variables[f'{column_name}_avg'] = float(column_metric['average'])
    
    return soda_variables