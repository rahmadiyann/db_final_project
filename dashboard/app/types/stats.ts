export interface ListeningStats {
  // Basic metrics
  totalMinutesListened: number;
  totalSongsPlayed: number;

  // Album completion
  albumCompletions: {
    albumTitle: string;
    artistName: string;
    completionPercentage: number;
    listeningStatus: string;
  }[];

  // Listening preferences
  durationPreference: {
    category: string;
    percentage: number;
  }[];

  explicitPreference: {
    explicit: boolean;
    percentage: number;
  }[];

  // Time-based stats
  dayDistribution: {
    dayOfWeek: string;
    playCount: number;
    songVarietyPercentage: number;
    artistVarietyPercentage: number;
  }[];

  hourDistribution: {
    hourOfDay: number;
    percentage: number;
  }[];

  // Streaks and records
  artistLongestStreak: {
    artistName: string;
    streak: number;
    dateFrom: string;
    dateUntil: string;
    totalMinutes: number;
  };

  longestListeningDay: {
    date: string;
    playCount: number;
  };

  // Song popularity
  popularityDistribution: {
    popularityRange: string;
    percentage: number;
  }[];

  // Release year distribution
  releaseYearDistribution: {
    year: number;
    playCount: number;
  }[];

  // Section 8: Weekly Listening Patterns
  sessionTypes: {
    sessionType: string;
    count: number;
    percentage: number;
  }[];
}
