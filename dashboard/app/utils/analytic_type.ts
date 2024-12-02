export type SpotifyAnalyticsResponse = {
  album_completion_rate: AlbumCompletionRate;
  album_release_year_play_count: AlbumReleaseYearPlayCount;
  explicit_preference: ExplicitPreference;
  hour_of_day_play_count: HourOfDayPlayCount;
  song_popularity_distribution: SongPopularityDistribution;
  seasonal_listening_analysis: SeasonalListeningAnalysis;
  listening_session_analysis: ListeningSessionAnalysis;
  song_duration_preference: SongDurationPreference;
};

type AlbumCompletionRate = {
  album_title: string;
  artist_name: string;
  total_tracks: number;
  unique_tracks_played: number;
  completion_percentage: number;
  listening_status: string;
};

type AlbumReleaseYearPlayCount = {
  release_year: number;
  play_count: number;
};

type ExplicitPreference = {
  explicit: boolean;
  play_count: number;
  percentage: number;
};

type HourOfDayPlayCount = {
  hour_of_day: number;
  play_count: number;
  percentage: number;
};

type SongPopularityDistribution = {
  popularity_range: string;
  play_count: number;
  percentage: number;
};

type SeasonalListeningAnalysis = {
  month: string;
  play_count: number;
  unique_songs: number;
  unique_artists: number;
  song_variety_percentage: number;
  artist_variety_percentage: number;
};

type ListeningSessionAnalysis = {
  session_type: string;
  count: number;
  percentage: number;
};

type SongDurationPreference = {
  duration_category: string;
  play_count: number;
  percentage: number;
};
