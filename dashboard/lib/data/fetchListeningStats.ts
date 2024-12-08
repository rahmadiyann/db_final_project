import { prisma } from "../prisma";
import { ListeningStats } from "../../app/types/stats";
import { cache } from "react";

// Use cache to dedupe requests during rendering but allow revalidation
export const fetchListeningStats = cache(async (): Promise<ListeningStats> => {
  try {
    // Force revalidation of data
    const baseStats = await prisma.statistics.findFirst();

    // Fetch all data with proper error handling
    const [
      albumCompletions,
      durationPrefs,
      explicitPrefs,
      dayDist,
      hourDist,
      artistStreak,
      longestDay,
      popDist,
      yearDist,
      sessionTypes,
    ] = await Promise.all([
      prisma.album_completion_analysis.findMany(),
      prisma.song_duration_preference.findMany(),
      prisma.explicit_preference.findMany(),
      prisma.day_of_week_listening_distribution.findMany(),
      prisma.hour_of_day_listening_distribution.findMany(),
      prisma.artist_longest_streak
        .findFirst({
          orderBy: { streak_days: "desc" },
        })
        .catch(() => null),
      prisma.longest_listening_day
        .findFirst({
          orderBy: { songs_played: "desc" },
        })
        .catch(() => null),
      prisma.song_popularity_distribution
        .findMany({
          orderBy: { popularity_bracket: "asc" },
        })
        .catch(() => []),
      prisma.album_release_year_play_count
        .findMany({
          orderBy: { release_year: "desc" },
        })
        .catch(() => []),
      prisma.session_between_songs.findMany().catch(() => []),
    ]);

    // If we have any data at all, return it
    if (
      (baseStats?.total_songs_played ?? 0) > 0 ||
      albumCompletions.length > 0
    ) {
      return {
        totalMinutesListened: Math.floor(
          Number(baseStats?.total_miliseconds ?? 0) / 60000
        ),
        totalSongsPlayed: baseStats?.total_songs_played ?? 0,
        albumCompletions: albumCompletions.map((ac) => ({
          albumTitle: ac.album_title,
          artistName: ac.artist_name,
          albumImageUrl: ac.album_image_url,
          completionPercentage: ac.completion_percentage,
          totalTracks: ac.total_tracks,
          uniqueTracksPlayed: ac.unique_tracks_played,
        })),
        durationPreference: durationPrefs.length
          ? durationPrefs.map((dp) => ({
              category: dp.duration_category,
              percentage: dp.percentage,
            }))
          : [
              { category: "Short (<3 min)", percentage: 33.33 },
              { category: "Medium (3-5 min)", percentage: 33.33 },
              { category: "Long (>5 min)", percentage: 33.34 },
            ],
        explicitPreference: explicitPrefs.length
          ? explicitPrefs.map((ep) => ({
              explicit: ep.explicit,
              percentage: ep.percentage,
            }))
          : [
              { explicit: true, percentage: 50 },
              { explicit: false, percentage: 50 },
            ],
        dayDistribution: dayDist.length
          ? dayDist.map((dd) => ({
              dayOfWeek: dd.day_of_week,
              playCount: dd.play_count,
              songVarietyPercentage: dd.song_variety_percentage,
              artistVarietyPercentage: dd.artist_variety_percentage,
            }))
          : generateDefaultDayDistribution(),
        hourDistribution: hourDist.length
          ? hourDist.map((hd) => ({
              hourOfDay: hd.hour_of_day,
              percentage: hd.percentage,
            }))
          : generateDefaultHourDistribution(),
        artistLongestStreak: artistStreak
          ? {
              artistId: artistStreak.artist_id,
              artistName: artistStreak.artist_name,
              artist_image_url: artistStreak.artist_image_url,
              streak: artistStreak.streak_days,
              dateFrom: artistStreak.date_from,
              dateUntil: artistStreak.date_until,
              totalMinutes: artistStreak.streak_days * 24 * 60,
            }
          : generateDefaultArtistStreak(),
        longestListeningDay: longestDay
          ? {
              date: longestDay.date.toISOString(),
              playCount: longestDay.songs_played,
            }
          : generateDefaultLongestDay(),
        popularityDistribution: popDist.length
          ? popDist.map((pd) => ({
              popularityRange: pd.popularity_range,
              percentage: pd.percentage,
            }))
          : generateDefaultPopularityDistribution(),
        releaseYearDistribution: yearDist.length
          ? yearDist.map((yd) => ({
              year: yd.release_year,
              playCount: yd.play_count,
            }))
          : generateDefaultReleaseYearDistribution(),
        sessionTypes: sessionTypes.length
          ? sessionTypes.map((st) => ({
              sessionType: st.session_type,
              count: st.count,
              percentage: st.percentage,
            }))
          : generateDefaultSessionTypes(),
      };
    }

    return generateDefaultStats();
  } catch (error) {
    console.error("Error fetching listening stats:", error);
    return generateDefaultStats();
  }
});

// Helper functions to generate default data
function generateDefaultDayDistribution() {
  const days = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
  ];
  return days.map((day) => ({
    dayOfWeek: day,
    playCount: 0,
    songVarietyPercentage: 0,
    artistVarietyPercentage: 0,
  }));
}

function generateDefaultHourDistribution() {
  return Array.from({ length: 24 }, (_, i) => ({
    hourOfDay: i,
    percentage: 100 / 24,
  }));
}

function generateDefaultArtistStreak() {
  return {
    artistId: "",
    artistName: "No listening data yet",
    artist_image_url: "/default-artist-image.jpg",
    streak: 0,
    dateFrom: new Date(),
    dateUntil: new Date(),
    totalMinutes: 0,
  };
}

function generateDefaultLongestDay() {
  return {
    date: new Date().toISOString(),
    playCount: 0,
  };
}

function generateDefaultPopularityDistribution() {
  return [
    { popularityRange: "Underground", percentage: 25 },
    { popularityRange: "Rising", percentage: 25 },
    { popularityRange: "Popular", percentage: 25 },
    { popularityRange: "Mainstream", percentage: 25 },
  ];
}

function generateDefaultReleaseYearDistribution() {
  const currentYear = new Date().getFullYear();
  return Array.from({ length: 5 }, (_, i) => ({
    year: currentYear - i,
    playCount: 0,
  }));
}

function generateDefaultSessionTypes() {
  return [
    { sessionType: "Focused", count: 0, percentage: 20 },
    { sessionType: "Background", count: 0, percentage: 20 },
    { sessionType: "Party", count: 0, percentage: 20 },
    { sessionType: "Chill", count: 0, percentage: 20 },
    { sessionType: "Workout", count: 0, percentage: 20 },
  ];
}

function generateDefaultStats(): ListeningStats {
  return {
    totalMinutesListened: 0,
    totalSongsPlayed: 0,
    albumCompletions: [],
    durationPreference: [
      { category: "Short (<3 min)", percentage: 33.33 },
      { category: "Medium (3-5 min)", percentage: 33.33 },
      { category: "Long (>5 min)", percentage: 33.34 },
    ],
    explicitPreference: [
      { explicit: true, percentage: 50 },
      { explicit: false, percentage: 50 },
    ],
    dayDistribution: generateDefaultDayDistribution(),
    hourDistribution: generateDefaultHourDistribution(),
    artistLongestStreak: generateDefaultArtistStreak(),
    longestListeningDay: generateDefaultLongestDay(),
    popularityDistribution: generateDefaultPopularityDistribution(),
    releaseYearDistribution: generateDefaultReleaseYearDistribution(),
    sessionTypes: generateDefaultSessionTypes(),
  };
}
