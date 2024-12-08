export interface ListeningStats {
  totalMinutesListened: number;
  totalSongsPlayed: number;
  albumCompletions: AlbumCompletion[];
  durationPreference: DurationPreference[];
  explicitPreference: ExplicitPreference[];
  dayDistribution: DayDistribution[];
  hourDistribution: HourDistribution[];
  artistLongestStreak: ArtistStreak;
  longestListeningDay: LongestDay;
  popularityDistribution: PopularityDistribution[];
  releaseYearDistribution: ReleaseYearDistribution[];
  sessionTypes: SessionType[];
}

export interface AlbumCompletion {
  albumTitle: string;
  artistName: string;
  albumImageUrl: string;
  completionPercentage: number;
  totalTracks: number;
  uniqueTracksPlayed: number;
}

export interface DurationPreference {
  category: string;
  percentage: number;
}

export interface ExplicitPreference {
  explicit: boolean;
  percentage: number;
}

export interface DayDistribution {
  dayOfWeek: string;
  playCount: number;
  songVarietyPercentage: number;
  artistVarietyPercentage: number;
}

export interface HourDistribution {
  hourOfDay: number;
  percentage: number;
}

export interface ArtistStreak {
  artistId: string;
  artistName: string;
  artist_image_url: string;
  streak: number;
  dateFrom: Date;
  dateUntil: Date;
  totalMinutes?: number;
}

export interface LongestDay {
  date: string;
  playCount: number;
}

export interface PopularityDistribution {
  popularityRange: string;
  percentage: number;
}

export interface ReleaseYearDistribution {
  year: number;
  playCount: number;
}

export interface SessionType {
  sessionType: string;
  count: number;
  percentage: number;
}
