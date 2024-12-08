from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import json
import requests
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import FactHistory, DimAlbum, DimArtist, DimSong

# Constants
BASE_URL = 'http://flask:8000'
STAGING_DIR = '/data/source2main/staging'
HIST_DIR = '/data/source2main/hist'

class DatabaseManager:
    def __init__(self):
        self.engine = create_engine(
            os.getenv('DATAENG_POSTGRES_URI'),
            pool_pre_ping=True,
            pool_recycle=300
        )
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )

    def get_session(self) -> Session:
        return self.SessionLocal()

class APIClient:
    @staticmethod
    def get_entity_data(entity_type: str, entity_id: str) -> Dict:
        response = requests.get(f'{BASE_URL}/{entity_type}?{entity_type}_id={entity_id}')
        return response.json()

    @classmethod
    def get_artist_data(cls, artist_id: str) -> Dict:
        return cls.get_entity_data('artist', artist_id)

    @classmethod
    def get_album_data(cls, album_id: str) -> Dict:
        return cls.get_entity_data('album', album_id)

    @classmethod
    def get_song_data(cls, song_id: str) -> Dict:
        return cls.get_entity_data('song', song_id)

class DataProcessor:
    def __init__(self, session: Session):
        self.session = session
        self.api_client = APIClient()

    def entity_exists(self, model_class, entity_id: str, id_field: str) -> bool:
        return self.session.query(model_class).filter(
            getattr(model_class, id_field) == entity_id
        ).first() is not None

    def process_landing_data(self, file_path: str) -> Dict:
        """Process landing data and stage it for further processing"""
        with open(file_path, 'r') as file:
            data = json.load(file)
            listening_data = data['data']
            fetch_time = data['cursor']
            last_played_at = data['last_played_at']
            
            new_artist_data = []
            new_album_data = []
            new_song_data = []
            existing_data = []
            artists_set = set()
            albums_set = set()
            songs_set = set()
            
            for record in listening_data:
                artist_id = record['artist_id']
                album_id = record['album_id'] 
                song_id = record['song_id']
                
                if not self.entity_exists(DimArtist, artist_id, 'artist_id') and artist_id not in artists_set:
                    artist_data = self.api_client.get_artist_data(artist_id)
                    new_artist_data.append(artist_data)
                    artists_set.add(artist_id)
                
                if not self.entity_exists(DimAlbum, album_id, 'album_id') and album_id not in albums_set:
                    album_data = self.api_client.get_album_data(album_id)
                    new_album_data.append(album_data)
                    albums_set.add(album_id)
                    
                if not self.entity_exists(DimSong, song_id, 'song_id') and song_id not in songs_set:
                    song_data = self.api_client.get_song_data(song_id)
                    new_song_data.append(song_data)
                    songs_set.add(song_id)
                
                existing_data.append(record)

            # Write new data to file for branch operator
            os.makedirs(STAGING_DIR, exist_ok=True)
            output_file = f'{STAGING_DIR}/{last_played_at}.json'
            
            played_at_start = existing_data[-1]['played_at']
            played_at_end = existing_data[0]['played_at']
            
            staging_data = {
                'artists_count': len(new_artist_data),
                'artists': new_artist_data,
                'albums_count': len(new_album_data),
                'albums': new_album_data,
                'songs_count': len(new_song_data),
                'songs': new_song_data,
                'listening_history_count': len(existing_data),
                'listening_history': existing_data,
                'last_fetch': fetch_time,
                'last_played_at': last_played_at,
                'played_at_start': played_at_start,
                'played_at_end': played_at_end,
                'staging_file_path': output_file
            }
            
            with open(output_file, 'w') as f:
                json.dump(staging_data, f)
            
            # Return metadata for XCom
            return json.dumps({
                "artists_count": len(new_artist_data),
                "albums_count": len(new_album_data),
                "songs_count": len(new_song_data),
                "listening_history_count": len(existing_data),
                "last_fetch": fetch_time,
                "last_played_at": last_played_at,
                "played_at_start": played_at_start,
                "played_at_end": played_at_end,
                "staging_file_path": output_file
            })

    def load_dimension(self, table: str, staging_metadata: str) -> None:
        """Load dimension tables with error handling and transaction management"""
        staging_metadata = json.loads(staging_metadata)
        staging_path = staging_metadata['staging_file_path']
        
        with open(staging_path, 'r') as file:
            data = json.load(file)
            
            model_map = {
                'artists': (DimArtist, data['artists']),
                'albums': (DimAlbum, data['albums']),
                'songs': (DimSong, data['songs'])
            }
            
            if table not in model_map:
                raise ValueError(f"Unknown table: {table}")
                
            model_class, records = model_map[table]
            
            if not records:
                print(f'No new data to insert into table {table}')
                return
                
            for record in records:
                try:
                    new_record = model_class(**record)
                    self.session.add(new_record)
                    self.session.commit()
                except Exception as e:
                    print(f"Error inserting {table} record: {str(e)}")
                    self.session.rollback()
                    continue

    def load_facts(self, staging_metadata: str) -> Dict:
        """Load fact table with error handling and transaction management"""
        staging_metadata = json.loads(staging_metadata)
        staging_path = staging_metadata['staging_file_path']
        
        with open(staging_path, 'r') as file:
            data = json.load(file)
            records_processed = 0
            
            for record in data['listening_history']:
                try:
                    fact = FactHistory(
                        song_id=record['song_id'],
                        album_id=record['album_id'],
                        artist_id=record['artist_id'],
                        played_at=record['played_at']
                    )
                    self.session.add(fact)
                    records_processed += 1
                    
                    # Commit in batches of 100 to optimize performance
                    if records_processed % 100 == 0:
                        self.session.commit()
                        
                except Exception as e:
                    print(f"Error inserting fact record: {str(e)}")
                    self.session.rollback()
                    continue
            
            # Commit any remaining records
            if records_processed % 100 != 0:
                self.session.commit()
                
            return {'table': 'fact', 'count': records_processed}

    def to_hist(self, staging_metadata: str) -> None:
        """Move processed data to historical storage"""
        staging_metadata = json.loads(staging_metadata)
        staging_path = staging_metadata['staging_file_path']
        last_fetch = staging_metadata['last_fetch']
        last_play = staging_metadata['last_played_at']
        last_play = int(last_play)  # Convert string timestamp to int
        
        # Create timestamp-based directory structure
        name = datetime.fromtimestamp(last_play / 1000)
        year = name.year
        month = name.month
        day = name.day
        
        with open(staging_path, 'r') as file:
            data = json.load(file)
            
            output_dir = f'{HIST_DIR}/{month}-{day}-{year}'
            os.makedirs(output_dir, exist_ok=True)
            
            # Write to historical storage
            with open(f'{output_dir}/listening_history_{last_play}.json', 'w') as f:
                json.dump(data, f)

# Helper functions
def convert_to_timestamp_ms(played_at: str) -> int:
    dt = datetime.fromisoformat(played_at.replace('Z', '+00:00'))
    return int(dt.timestamp() * 1000)

def convert_to_datetime_utc(time: str) -> datetime:
    return datetime.fromisoformat(time) - timedelta(hours=8)

# Initialize global instances
db_manager = DatabaseManager()
session = db_manager.get_session()
data_processor = DataProcessor(session)

# Export the functions with better organization
landing2staging = data_processor.process_landing_data
load_dimension_tables = data_processor.load_dimension
load_fact_table = data_processor.load_facts
to_hist = data_processor.to_hist