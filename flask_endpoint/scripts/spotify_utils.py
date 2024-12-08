import logging
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
from sqlalchemy.orm import Session
from scripts.models import Token
import time
from datetime import datetime
import os

logger = logging.getLogger(__name__)

scope = 'user-read-recently-played user-library-read'
client_id = os.getenv('SPOTIFY_CLIENT_ID')
client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
redirect_uri = 'http://localhost:8000/callback'
auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(auth_manager=auth_manager)

def create_spotify_oauth():
    """
    Create Spotify OAuth object.
    
    Returns:
        SpotifyOAuth: Spotify OAuth object
    """
    return SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
        scope=scope
    )
    
def save_token_info(session: Session, token_info: dict):
    """
    Save token info to database.
    
    Args:
        session (Session): SQLAlchemy Database session
        token_info (dict): Token info
    """
    session.add(Token(
        access_token=token_info['access_token'],
        refresh_token=token_info['refresh_token'],
        expires_at=token_info['expires_at']
    ))
    session.commit()
    
def load_access_token(session: Session):
    """
    Load access token from database.
    
    Args:
        session (Session): SQLAlchemy Database session
        
    Returns:
        str: Access token
    """
    token = session.query(Token).first()
    is_expired = token.expires_at - int(time.time()) < 60
    
    if is_expired:
        sp_oauth = create_spotify_oauth()
        token_info = sp_oauth.refresh_access_token(token.refresh_token)
        save_token_info(session, token_info)
    
    return token.access_token

def iso_to_unix_ms(iso_string):
    """
    Convert ISO format datetime string to Unix milliseconds.
    
    Args:
        iso_string (str): DateTime string in ISO format (e.g. "2024-11-29T16:20:59.368Z")
        
    Returns:
        int: Unix timestamp in milliseconds
    """
    dt = datetime.fromisoformat(iso_string.replace('Z', '+00:00'))
    return int(dt.timestamp() * 1000)
    
def get_recent_played(session: Session, limit: int = 20, last_fetch_time: int = 0) -> dict | None:
    """
    Get recent played songs from Spotify API.
    
    Args:
        session (Session): SQLAlchemy Database session

    Returns:
        dict | None: Recent played songs data
    """
    access_token = load_access_token(session)
    sp = spotipy.Spotify(auth=access_token)
    # last_fetched = session.query(Token).first().last_fetched
    try:
        song_data = sp.current_user_recently_played(after=last_fetch_time, limit=limit)
        if song_data['items'] == []:
            session.query(Token).update({'last_fetched': (int(time.time()) * 1000)})
            session.commit()
            return None
        session.query(Token).update({'last_fetched': iso_to_unix_ms(song_data['items'][0]['played_at'])})
        session.commit()
        return song_data
    except Exception as e:
        logger.error(f"Error fetching recent played: {e}")
        return None

def get_song_detail(session: Session, song_id: str) -> dict | None:
    """
    Get song detail from Spotify API.
    
    Args:
        session (Session): SQLAlchemy Database session
        song_id (str): Song ID

    Returns:
        dict | None: Song detail
    """
    access_token = load_access_token(session)
    sp = spotipy.Spotify(auth=access_token)
    try:
        data = sp.track(song_id)
        name, disc_number, duration_ms, explicit, external_urls, preview_url, popularity = data['name'], data['disc_number'], data['duration_ms'], data['explicit'], data['external_urls']['spotify'], data['preview_url'], data['popularity']
        return {
            'song_id': song_id,
            'title': name,
            'disc_number': disc_number,
            'duration_ms': duration_ms,
            'explicit': explicit,
            'external_url': external_urls,
            'preview_url': preview_url,
            'popularity': popularity
        }
    except Exception as e:
        logger.error(f"Error fetching song detail: {e}")
        return None

def get_artist_detail(session: Session, artist_id: str) -> dict | None:
    """
    Get artist detail from Spotify API.
    
    Args:
        session (Session): SQLAlchemy Database session
        artist_id (str): Artist ID

    Returns:
        dict | None: Artist detail
    """
    access_token = load_access_token(session)
    sp = spotipy.Spotify(auth=access_token)
    try:
        data = sp.artist(artist_id)
        name, external_url, follower_count, image_url, popularity = data['name'], data['external_urls']['spotify'], data['followers']['total'], data['images'][0]['url'], data['popularity']
        return {
            'artist_id': artist_id,
            'name': name,
            'external_url': external_url,
            'follower_count': follower_count,
            'image_url': image_url,
            'popularity': popularity
        }
    except Exception as e:
        logger.error(f"Error fetching artist detail: {e}")
        return None

def get_album_detail(session: Session, album_id: str) -> dict | None:
    """
    Get album detail from Spotify API.
    
    Args:
        session (Session): SQLAlchemy Database session
        album_id (str): Album ID

    Returns:
        dict | None: Album detail
    """
    access_token = load_access_token(session)
    sp = spotipy.Spotify(auth=access_token)
    try:
        data = sp.album(album_id)
        name, total_tracks, release_date, external_urls, image_url, label, popularity = data['name'], data['total_tracks'], data['release_date'], data['external_urls']['spotify'], data['images'][0]['url'], data['label'], data['popularity']
        return {
            'album_id': album_id,
            'title': name,
            'total_tracks': total_tracks,
            'release_date': release_date,
            'external_url': external_urls,
            'image_url': image_url,
            'label': label,
            'popularity': popularity
        }
    except Exception as e:
        logger.error(f"Error fetching album detail: {e}")
        return None

def get_callback(session: Session, code: str):
    """
    Get callback from Spotify API.
    
    Args:
        session (Session): SQLAlchemy Database session
        code (str): Authorization code

    Returns:
        dict: Token info
    """
    token_info = create_spotify_oauth().get_access_token(code)
    save_token_info(session, token_info)
    return token_info

def get_auth_url():
    """
    Get authorization URL from Spotify API.
    
    Returns:
        str: Authorization URL
    """
    return create_spotify_oauth().get_authorize_url()

def get_listening_stats(session: Session):
    pass