from flask import Flask, jsonify, request, redirect, url_for, session
from scripts.spotify_utils import get_album_detail, get_artist_detail, get_auth_url, get_callback, get_recent_played, get_song_detail
from scripts.db_utils import session as db_session
from scripts.models import Token
import secrets
import logging

logger = logging.getLogger(__name__)
app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
curr_session = db_session
TOKEN_INFO = ''

@app.route('/')
def homepage():
    user = curr_session.query(Token).first()
    if user:
        html = f"""
        <h1>Logged in. Access token saved.</h1>
        <a href="/logout">Log out</a>
        """
    else:
        html = f"""
        <h1>Not logged in.</h1>
        <a href="/login">Login</a>
        """
    return html

@app.route('/login', methods=['GET'])
def login():
    auth_url = get_auth_url()
    return redirect(auth_url)

@app.route('/logout', methods=['GET'])
def logout():
    curr_session.query(Token).delete()
    curr_session.commit()
    session.clear()
    return redirect(url_for('homepage', _external=True))

@app.route('/callback')
def callback():
    session.clear()
    code = request.args.get('code')
    token_info = get_callback(curr_session, code)
    session[TOKEN_INFO] = token_info
    return redirect(url_for('homepage', _external=True),)

@app.route('/recent_played')
def recent_played():
    data = get_recent_played(curr_session)
    if not data:
        return jsonify({'error': 'No recent played songs'}), 404
    
    datas = []
    for item in data['items']:
        played_at = item['played_at']
        song_id = item['track']['id']
        album_id = item['track']['album']['id']
        artist_id = item['track']['artists'][0]['id']
        songs_detail = get_song_detail(curr_session, song_id)
        albums_detail = get_album_detail(curr_session, album_id)
        artists_detail = get_artist_detail(curr_session, artist_id)
        datas.append({
            'played_at': played_at,
            'track': songs_detail,
            'album': albums_detail,
            'artist': artists_detail
        })
    return jsonify(datas), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)