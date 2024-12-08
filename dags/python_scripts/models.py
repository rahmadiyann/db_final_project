from sqlalchemy import Column, Integer, String, BigInteger, Boolean, DateTime, ForeignKey, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Token(Base):
    __tablename__ = 'tokens'

    id = Column(Integer, primary_key=True)
    access_token = Column(String(512))
    refresh_token = Column(String(512))
    last_fetched = Column(BigInteger)
    expires_at = Column(Integer)

    def __repr__(self):
        return f"<Token(id={self.id}, access_token={self.access_token}, refresh_token={self.refresh_token}, last_fetched={self.last_fetched}, expires_at={self.expires_at})>"
    
class DimSong(Base):
    __tablename__ = 'dim_song'

    song_id = Column(String, primary_key=True)
    title = Column(String)
    disc_number = Column(Integer)
    duration_ms = Column(BigInteger)
    explicit = Column(Boolean)
    external_url = Column(String)
    preview_url = Column(String)
    popularity = Column(Integer)
    added_at = Column(DateTime, nullable=False, default=func.now())
    
    def __repr__(self):
        return f"<DimSong(song_id={self.song_id}, title={self.title}, disc_number={self.disc_number}, duration_ms={self.duration_ms}, explicit={self.explicit}, external_url={self.external_url}, preview_url={self.preview_url}, popularity={self.popularity})>"
    
class DimAlbum(Base):
    __tablename__ = 'dim_album'

    album_id = Column(String, primary_key=True)
    title = Column(String)
    total_tracks = Column(Integer)
    release_date = Column(DateTime)
    external_url = Column(String)
    image_url = Column(String)
    label = Column(String)
    popularity = Column(Integer)
    added_at = Column(DateTime, nullable=False, default=func.now())
    
    def __repr__(self):
        return f"<DimAlbum(album_id={self.album_id}, title={self.title}, total_tracks={self.total_tracks}, release_date={self.release_date}, external_url={self.external_url}, image_url={self.image_url}, label={self.label}, popularity={self.popularity})>"

class DimArtist(Base):
    __tablename__ = 'dim_artist'

    artist_id = Column(String, primary_key=True)
    name = Column(String)
    external_url = Column(String)
    follower_count = Column(Integer)
    image_url = Column(String)
    popularity = Column(Integer)
    added_at = Column(DateTime, nullable=False, default=func.now())
    
    def __repr__(self):
        return f"<DimArtist(artist_id={self.artist_id}, name={self.name}, external_url={self.external_url}, follower_count={self.follower_count}, image_url={self.image_url}, popularity={self.popularity})>"
    
class FactHistory(Base):
    __tablename__ = 'fact_history'

    id = Column(Integer, primary_key=True)
    song_id = Column(String, ForeignKey('dim_song.song_id'), nullable=False)
    artist_id = Column(String, ForeignKey('dim_artist.artist_id'), nullable=False)
    album_id = Column(String, ForeignKey('dim_album.album_id'), nullable=False)
    played_at = Column(DateTime, nullable=False)
    added_at = Column(DateTime, nullable=False, default=func.now())

    song = relationship("DimSong", backref="fact_histories")
    artist = relationship("DimArtist", backref="fact_histories")
    album = relationship("DimAlbum", backref="fact_histories")