import sys
import argparse
from utils.etl_base import SparkETLBase
from transformations.hour_of_day_play_count import HourOfDayPlayCountETL
from transformations.popularity_pref import PopularityPrefETL
from transformations.session_between_songs import SessionBetweenSongsETL
from transformations.song_dur_pref import SongDurPrefETL
from transformations.album_completion_rate import AlbumCompletionETL
from transformations.album_release_year_play_count import AlbumReleaseYearETL
from transformations.day_of_week import DayOfWeekETL
from transformations.explicit_pref import ExplicitPreferenceETL
from spark_scripts.transformations.statistics import StatisticsETL
from transformations.artist_longest_streak import ArtistLongestStreak
from transformations.longest_listening_day import BiggestListeningDateETL
from transformations.top_played_song_detail import TopSongDetail


# Add base ETL for source tables
SOURCE_TABLES = {
    'dim_artist': SparkETLBase,
    'dim_song': SparkETLBase,
    'dim_album': SparkETLBase,
    'fact_history': SparkETLBase,
}

ANALYSIS_TABLES = {
    'analysis.album_completion_rate': AlbumCompletionETL,
    'analysis.album_release_year_play_count': AlbumReleaseYearETL,
    'analysis.day_of_week': DayOfWeekETL,
    'analysis.explicit_preference': ExplicitPreferenceETL,
    'analysis.hour_of_day_play_count': HourOfDayPlayCountETL,
    'analysis.popularity_pref': PopularityPrefETL,
    'analysis.session_between_songs': SessionBetweenSongsETL,
    'analysis.song_dur_pref': SongDurPrefETL,
    'metrics.statistics': StatisticsETL,
    'metrics.artist_longest_streak': ArtistLongestStreak,
    'metrics.longest_listening_day': BiggestListeningDateETL,
    'metrics.top_played_song': TopSongDetail
}


# Combine both mappings
ETL_MAPPING = {**SOURCE_TABLES, **ANALYSIS_TABLES}

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", required=True)
    parser.add_argument("--destination", required=True)
    parser.add_argument("--table", required=True)
    parser.add_argument("--transform", default=False, action="store_true")
    return parser.parse_args()

def main():
    args = get_args()
    
    etl_class = ETL_MAPPING.get(args.table)
    print(f"table: {args.table}, etl_class: {etl_class}")
    if not etl_class:
        print(f"No ETL class found for table {args.table}")
        sys.exit(1)
        
    etl = etl_class(
        f"{args.table}",
        args.stage,
        args.destination,
        args.table,
        args.transform
    )
    etl.run()

if __name__ == "__main__":
    main() 