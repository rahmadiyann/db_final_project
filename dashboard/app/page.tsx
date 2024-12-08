"use client";

import { prisma } from "../lib/prisma";
import dynamic from "next/dynamic";
import { ListeningStats } from "./types/stats";

const StatisticsPage = dynamic(() => import("./components/StatisticsPage"), {
  ssr: false,
});

async function fetchListeningStats(): Promise<ListeningStats> {
  // Fetch base statistics
  const baseStats = await prisma.statistics.findFirst();

  // Fetch album completions
  const albumCompletions = await prisma.album_completion_analysis.findMany();

  // Fetch duration preferences
  const durationPrefs = await prisma.song_duration_preference.findMany();

  // Fetch explicit preferences
  const explicitPrefs = await prisma.explicit_preference.findMany();

  // Fetch day distribution
  const dayDist = await prisma.day_of_week_listening_distribution.findMany();

  // Fetch hour distribution
  const hourDist = await prisma.hour_of_day_listening_distribution.findMany();

  // Fetch artist streak
  const artistStreak = await prisma.artist_longest_streak.findFirst({
    orderBy: { streak_days: "desc" },
  });

  // Fetch longest day
  const longestDay = await prisma.longest_listening_day.findFirst({
    orderBy: { songs_played: "desc" },
  });

  // Fetch popularity distribution
  const popDist = await prisma.song_popularity_distribution.findMany({
    orderBy: { popularity_bracket: "asc" },
  });

  // Fetch release year distribution
  const yearDist = await prisma.album_release_year_play_count.findMany({
    orderBy: { release_year: "desc" },
  });

  // Fetch session types
  const sessionTypes = await prisma.session_between_songs.findMany();

  return {
    totalMinutesListened: Math.floor(
      Number(baseStats?.total_miliseconds || 0) / 60000
    ),
    totalSongsPlayed: baseStats?.total_songs_played || 0,

    albumCompletions: albumCompletions.map((ac) => ({
      albumTitle: ac.album_title,
      artistName: ac.artist_name,
      completionPercentage: ac.completion_percentage,
      listeningStatus: ac.listening_status,
    })),

    durationPreference: durationPrefs.map((dp) => ({
      category: dp.duration_category,
      percentage: dp.percentage,
    })),

    explicitPreference: explicitPrefs.map((ep) => ({
      explicit: ep.explicit,
      percentage: ep.percentage,
    })),

    dayDistribution: dayDist.map((dd) => ({
      dayOfWeek: dd.day_of_week,
      playCount: dd.play_count,
      songVarietyPercentage: dd.song_variety_percentage,
      artistVarietyPercentage: dd.artist_variety_percentage,
    })),

    hourDistribution: hourDist.map((hd) => ({
      hourOfDay: hd.hour_of_day,
      percentage: hd.percentage,
    })),

    artistLongestStreak: artistStreak
      ? {
          artistName: artistStreak.artist_name,
          streak: artistStreak.streak_days,
          dateFrom: artistStreak.date_from.toISOString(),
          dateUntil: artistStreak.date_until.toISOString(),
          totalMinutes: artistStreak.streak_days * 24 * 60,
        }
      : {
          artistName: "No streak found",
          streak: 0,
          dateFrom: new Date().toISOString(),
          dateUntil: new Date().toISOString(),
          totalMinutes: 0,
        },

    longestListeningDay: longestDay
      ? {
          date: longestDay.date.toISOString(),
          playCount: longestDay.songs_played,
        }
      : {
          date: new Date().toISOString(),
          playCount: 0,
        },

    popularityDistribution: popDist.map((pd) => ({
      popularityRange: pd.popularity_range,
      percentage: pd.percentage,
    })),

    releaseYearDistribution: yearDist.map((yd) => ({
      year: yd.release_year,
      playCount: yd.play_count,
    })),

    sessionTypes: sessionTypes.map((st) => ({
      sessionType: st.session_type,
      count: st.count,
      percentage: st.percentage,
    })),
  };
}

export default async function Home() {
  const stats = await fetchListeningStats();
  return <StatisticsPage stats={stats} />;
}
