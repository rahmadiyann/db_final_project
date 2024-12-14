# Flask API Endpoint

This directory contains the Flask API endpoint code for the Spotify data pipeline. The API serves as an interface to fetch data from the Spotify API and store it in the PostgreSQL database.

## Files

- `app.py`: The main Flask application file that defines the API routes and handlers.
- `requirements.txt`: The list of Python dependencies required for the Flask application.
- `scripts/`: Directory containing utility scripts used by the Flask application.
  - `db_utils.py`: Utility functions for interacting with the PostgreSQL database.
  - `models.py`: SQLAlchemy models representing the database tables.
  - `spotify_utils.py`: Utility functions for interacting with the Spotify API.

## API Routes

The Flask API provides the following routes:

- `/`: Homepage route that displays the login status and provides links to login or logout.
- `/login`: Initiates the Spotify OAuth login flow by redirecting the user to the Spotify authorization page.
- `/logout`: Logs out the user by clearing the session and deleting the access token from the database.
- `/callback`: Callback route that handles the Spotify OAuth callback and saves the access token to the database.
- `/recent_played`: Fetches the user's recently played songs from the Spotify API.
- `/song`: Fetches the details of a specific song from the Spotify API.
- `/album`: Fetches the details of a specific album from the Spotify API.
- `/artist`: Fetches the details of a specific artist from the Spotify API.
- `/spotify_analytics`: (To be implemented) Fetches listening statistics from the Spotify API.

## Setup and Usage

1. Install the required Python dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Set the following environment variables:

   - `SPOTIFY_CLIENT_ID`: Spotify API client ID.
   - `SPOTIFY_CLIENT_SECRET`: Spotify API client secret.
   - `DATAENG_POSTGRES_URI`: URI for connecting to the PostgreSQL database.

3. Run the Flask application:

   ```bash
   python app.py
   ```

   The API will be accessible at `http://localhost:8000`.

4. Use the API routes to interact with the Spotify data and store it in the PostgreSQL database.

## Database Models

The Flask application uses SQLAlchemy to define the database models. The models are defined in the `scripts/models.py` file and include:

- `Token`: Represents the access token and refresh token for the Spotify API.
- `DimSong`: Represents a song in the database.
- `DimAlbum`: Represents an album in the database.
- `DimArtist`: Represents an artist in the database.
- `FactHistory`: Represents the listening history fact table.
- Various analysis tables: `ArtistLongestStreak`, `LongestListeningDay`, `Statistics`, `TopPlayedSong`, `AlbumCompletionAnalysis`, `AlbumReleaseYearPlayCount`, `DayOfWeekListeningDistribution`, `ExplicitPreference`, `HourOfDayListeningDistribution`, `SessionBetweenSongs`, `SongDurationPreference`, `SongPopularityDistribution`.

## Deployment

The Flask API can be deployed using a WSGI server like Gunicorn. The `Dockerfile.flask` file in the `docker` directory provides a Dockerfile for building a Docker image of the Flask application.

To deploy the Flask API using Docker Compose, refer to the `docker-compose-flask.yml` file in the `docker` directory.

Make sure to set the required environment variables and configure the PostgreSQL connection details before deploying the application.
