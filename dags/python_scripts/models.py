from sqlalchemy import Column, Integer, String, BigInteger, Boolean, DateTime, ForeignKey, Text, Date, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Token(Base):
    """
    Token model.
    """
    __tablename__ = 'tokens'
    __table_args__ = {'schema': 'public'}

    id = Column(Integer, primary_key=True, autoincrement=True)
    access_token = Column(String(512), nullable=True)
    refresh_token = Column(String(512), nullable=True)
    last_fetched = Column(BigInteger, nullable=True)
    expires_at = Column(Integer, nullable=True)

    def __repr__(self):
        return f"<Token(id={self.id}, access_token={self.access_token}, refresh_token={self.refresh_token}, last_fetched={self.last_fetched}, expires_at={self.expires_at})>"
    
class DimSong(Base):
    """
    Song model.
    """
    __tablename__ = 'dim_song'
    __table_args__ = {'schema': 'public'}
    
    song_id = Column(String, primary_key=True)
    title = Column(String)
    disc_number = Column(Integer)
    duration_ms = Column(BigInteger)
    explicit = Column(Boolean)
    external_url = Column(String)
    preview_url = Column(String)
    popularity = Column(Integer)
    play_count = Column(Integer, default=0, nullable=True)
    
    def __repr__(self):
        return f"<DimSong(song_id={self.song_id}, title={self.title}, disc_number={self.disc_number}, duration_ms={self.duration_ms}, explicit={self.explicit}, external_url={self.external_url}, preview_url={self.preview_url}, popularity={self.popularity})>"
    
class DimAlbum(Base):
    """
    Album model.
    """
    __tablename__ = 'dim_album'
    __table_args__ = {'schema': 'public'}
    
    album_id = Column(String, primary_key=True)
    title = Column(String)
    total_tracks = Column(Integer)
    release_date = Column(DateTime)
    external_url = Column(String)
    image_url = Column(String)
    label = Column(String)
    popularity = Column(Integer)
    play_count = Column(Integer, default=0, nullable=True)
    
    def __repr__(self):
        return f"<DimAlbum(album_id={self.album_id}, title={self.title}, total_tracks={self.total_tracks}, release_date={self.release_date}, external_url={self.external_url}, image_url={self.image_url}, label={self.label}, popularity={self.popularity})>"

class DimArtist(Base):
    """
    Artist model.
    """
    __tablename__ = 'dim_artist'
    __table_args__ = {'schema': 'public'}
    
    artist_id = Column(String, primary_key=True)
    name = Column(String)
    external_url = Column(String)
    follower_count = Column(Integer)
    image_url = Column(String)
    popularity = Column(Integer)
    play_count = Column(Integer, default=0, nullable=True)
    
    def __repr__(self):
        return f"<DimArtist(artist_id={self.artist_id}, name={self.name}, external_url={self.external_url}, follower_count={self.follower_count}, image_url={self.image_url}, popularity={self.popularity})>"
    
class FactHistory(Base):
    """
    Fact history model.
    """
    __tablename__ = 'fact_history'
    __table_args__ = {'schema': 'public'}
    
    id = Column(Integer, primary_key=True)
    song_id = Column(String, ForeignKey('public.dim_song.song_id'), nullable=False)
    artist_id = Column(String, ForeignKey('public.dim_artist.artist_id'), nullable=False)
    album_id = Column(String, ForeignKey('public.dim_album.album_id'), nullable=False)
    played_at = Column(DateTime, nullable=False)

    song = relationship("DimSong", backref="fact_histories")
    artist = relationship("DimArtist", backref="fact_histories")
    album = relationship("DimAlbum", backref="fact_histories")
    

class ArtistLongestStreak(Base):
    __tablename__ = 'artist_longest_streak'
    __table_args__ = {'schema': 'metrics'}

    artist_id = Column(Text, primary_key=True)
    artist_name = Column(Text, nullable=False)
    artist_image_url = Column(Text)
    streak_days = Column(BigInteger, nullable=False)
    date_from = Column(Date, nullable=False)
    date_until = Column(Date, nullable=False)


class LongestListeningDay(Base):
    __tablename__ = 'longest_listening_day'
    __table_args__ = {'schema': 'metrics'}

    date = Column(Date, primary_key=True)
    total_miliseconds = Column(BigInteger, nullable=False)
    songs_played = Column(BigInteger, nullable=False)


class Statistics(Base):
    __tablename__ = 'statistics'
    __table_args__ = {'schema': 'metrics'}

    total_miliseconds = Column(BigInteger, primary_key=True)
    total_songs_played = Column(BigInteger, nullable=False)


class TopPlayedSong(Base):
    __tablename__ = 'top_played_song'
    __table_args__ = {'schema': 'metrics'}

    song_id = Column(Text, primary_key=True)
    song_title = Column(Text, nullable=False)
    artist_id = Column(Text, nullable=False)
    artist_name = Column(Text, nullable=False)
    artist_image_url = Column(Text)
    play_count = Column(BigInteger, nullable=False)
    first_played_at = Column(DateTime, nullable=False)
    last_played_at = Column(DateTime, nullable=False)


class AlbumCompletionAnalysis(Base):
    __tablename__ = 'album_completion_analysis'
    __table_args__ = {'schema': 'analysis'}

    album_title = Column(Text, primary_key=True)
    artist_name = Column(Text, nullable=False)
    album_image_url = Column(Text, nullable=False)
    total_tracks = Column(Integer, nullable=False)
    unique_tracks_played = Column(BigInteger, nullable=False)
    completion_percentage = Column(Float(53), nullable=False)
    listening_status = Column(Text, nullable=False)


class AlbumReleaseYearPlayCount(Base):
    __tablename__ = 'album_release_year_play_count'
    __table_args__ = {'schema': 'analysis'}

    release_year = Column(Integer, primary_key=True)
    play_count = Column(BigInteger, nullable=False)


class DayOfWeekListeningDistribution(Base):
    __tablename__ = 'day_of_week_listening_distribution'
    __table_args__ = {'schema': 'analysis'}

    day_of_week = Column(Text, primary_key=True)
    play_count = Column(BigInteger, nullable=False)
    unique_songs = Column(BigInteger, nullable=False)
    unique_artists = Column(BigInteger, nullable=False)
    song_variety_percentage = Column(Float(53), nullable=False)
    artist_variety_percentage = Column(Float(53), nullable=False)


class ExplicitPreference(Base):
    __tablename__ = 'explicit_preference'
    __table_args__ = {'schema': 'analysis'}

    explicit = Column(Boolean, primary_key=True)
    play_count = Column(BigInteger, nullable=False)
    percentage = Column(Float(53), nullable=False)


class HourOfDayListeningDistribution(Base):
    __tablename__ = 'hour_of_day_listening_distribution'
    __table_args__ = {'schema': 'analysis'}

    hour_of_day = Column(Integer, primary_key=True)
    play_count = Column(BigInteger, nullable=False)
    percentage = Column(Float(53), nullable=False)


class SessionBetweenSongs(Base):
    __tablename__ = 'session_between_songs'
    __table_args__ = {'schema': 'analysis'}

    session_type = Column(Text, primary_key=True)
    count = Column(BigInteger, nullable=False)
    percentage = Column(Float(53), nullable=False)


class SongDurationPreference(Base):
    __tablename__ = 'song_duration_preference'
    __table_args__ = {'schema': 'analysis'}

    duration_category = Column(Text, primary_key=True)
    play_count = Column(BigInteger, nullable=False)
    percentage = Column(Float(53), nullable=False)


class SongPopularityDistribution(Base):
    __tablename__ = 'song_popularity_distribution'
    __table_args__ = {'schema': 'analysis'}

    popularity_bracket = Column(Integer, primary_key=True)
    play_count = Column(BigInteger, nullable=False)
    popularity_range = Column(Text, nullable=False)
    percentage = Column(Float(53), nullable=False)
