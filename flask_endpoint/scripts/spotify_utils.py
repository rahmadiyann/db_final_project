import logging
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
from sqlalchemy.orm import Session
from scripts.models import Token
import time
from datetime import datetime

logger = logging.getLogger(__name__)

scope = 'user-read-recently-played user-library-read'
client_id = '1c9c9fe9723045b58a3dd31c2a7be91f'
client_secret = '577ae584282b4e539dfe893134b74430'
redirect_uri = 'http://localhost:8000/callback'
auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(auth_manager=auth_manager)

def create_spotify_oauth():
    return SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
        scope=scope
    )
    
def save_token_info(session: Session, token_info: dict):
    session.add(Token(
        access_token=token_info['access_token'],
        refresh_token=token_info['refresh_token'],
        expires_at=token_info['expires_at']
    ))
    session.commit()
    
def load_access_token(session: Session):
    token = session.query(Token).first()
    is_expired = token.expires_at - int(time.time()) < 600
    
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
    
def get_recent_played(session: Session):
    access_token = load_access_token(session)
    sp = spotipy.Spotify(auth=access_token)
    last_fetched = session.query(Token).first().last_fetched
    data = sp.current_user_recently_played(after=last_fetched)
    if data['items'] == []:
        session.query(Token).update({'last_fetched': int(time.time())})
        session.commit()
        return None
    session.query(Token).update({'last_fetched': iso_to_unix_ms(data['items'][0]['played_at'])})
    session.commit()
    return data

def get_song_detail(session: Session, song_id: str):
    access_token = load_access_token(session)
    sp = spotipy.Spotify(auth=access_token)
    data = sp.track(song_id)
    name, disc_number, duration_ms, explicit, external_urls, preview_url, popularity = data['name'], data['disc_number'], data['duration_ms'], data['explicit'], data['external_urls']['spotify'], data['preview_url'], data['popularity']
    return {
        'name': name,
        'disc_number': disc_number,
        'duration_ms': duration_ms,
        'explicit': explicit,
        'external_urls': external_urls,
        'preview_url': preview_url,
        'popularity': popularity
    }

def get_artist_detail(session: Session, artist_id: str):
    access_token = load_access_token(session)
    sp = spotipy.Spotify(auth=access_token)
    data = sp.artist(artist_id)
    name, external_urls, followers, images, popularity = data['name'], data['external_urls']['spotify'], data['followers']['total'], data['images'], data['popularity']
    return {
        'name': name,
        'external_urls': external_urls,
        'followers': followers,
        'images': images,
        'popularity': popularity
    }

def get_album_detail(session: Session, album_id: str):
    access_token = load_access_token(session)
    sp = spotipy.Spotify(auth=access_token)
    data = sp.album(album_id)
    name, total_tracks, external_urls, images, label, popularity = data['name'], data['total_tracks'], data['external_urls']['spotify'], data['images'], data['label'], data['popularity']
    return {
        'name': name,
        'total_tracks': total_tracks,
        'external_urls': external_urls,
        'images': images,
        'label': label,
        'popularity': popularity
    }

def get_callback(session: Session, code: str):
    token_info = create_spotify_oauth().get_access_token(code)
    save_token_info(session, token_info)
    return token_info

def get_auth_url():
    return create_spotify_oauth().get_authorize_url()
