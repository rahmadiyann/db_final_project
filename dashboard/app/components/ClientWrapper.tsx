"use client";

import dynamic from "next/dynamic";
import { ListeningStats } from "../types/stats";
import { useEffect, useState, useRef } from "react";
import { motion, useScroll, useTransform } from "framer-motion";

// Loading component
const LoadingSection = () => (
  <div className="min-h-screen flex items-center justify-center bg-black text-white">
    <div className="text-2xl font-bold animate-pulse">Loading...</div>
  </div>
);

// Dynamically import chart components with ssr: false and loading state
const Overview = dynamic(() => import("./statistics/Overview"), {
  ssr: false,
  loading: () => <LoadingSection />,
});
const DailyRhythm = dynamic(() => import("./statistics/DailyRhythm"), {
  ssr: false,
  loading: () => <LoadingSection />,
});
const ArtistStreak = dynamic(() => import("./statistics/ArtistStreak"), {
  ssr: false,
  loading: () => <LoadingSection />,
});
const AlbumCompletion = dynamic(() => import("./statistics/AlbumCompletion"), {
  ssr: false,
  loading: () => <LoadingSection />,
});
const ListeningPreferences = dynamic(
  () => import("./statistics/ListeningPreferences"),
  { ssr: false, loading: () => <LoadingSection /> }
);
const PopularityDistribution = dynamic(
  () => import("./statistics/PopularityDistribution"),
  { ssr: false, loading: () => <LoadingSection /> }
);
const WeeklyPattern = dynamic(() => import("./statistics/WeeklyPattern"), {
  ssr: false,
  loading: () => <LoadingSection />,
});
const ListeningSessions = dynamic(
  () => import("./statistics/ListeningSessions"),
  { ssr: false, loading: () => <LoadingSection /> }
);
const LongestDay = dynamic(() => import("./statistics/LongestDay"), {
  ssr: false,
  loading: () => <LoadingSection />,
});
const GenreDistribution = dynamic(
  () => import("./statistics/GenreDistribution"),
  { ssr: false, loading: () => <LoadingSection /> }
);
const ReleaseYearDistribution = dynamic(
  () => import("./statistics/ReleaseYearDistribution"),
  { ssr: false, loading: () => <LoadingSection /> }
);

const FadeSection = ({ children }: { children: React.ReactNode }) => {
  const ref = useRef(null);
  const { scrollYProgress } = useScroll({
    target: ref,
    offset: ["start end", "end start"],
  });

  const opacity = useTransform(
    scrollYProgress,
    [0, 0.1, 0.9, 1], // Scroll progress points
    [0, 1, 1, 0] // Corresponding opacity values
  );

  return (
    <motion.div
      ref={ref}
      style={{ opacity }}
      className="min-h-screen flex items-center justify-center"
    >
      {children}
    </motion.div>
  );
};

export default function ClientWrapper({ stats }: { stats: ListeningStats }) {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    return <LoadingSection />;
  }

  return (
    <div className="bg-black text-white">
      <FadeSection>
        <Overview totalMinutesListened={stats.totalMinutesListened} />
      </FadeSection>
      <FadeSection>
        <LongestDay longestListeningDay={stats.longestListeningDay} />
      </FadeSection>
      <FadeSection>
        <DailyRhythm hourDistribution={stats.hourDistribution} />
      </FadeSection>
      <FadeSection>
        <ArtistStreak artistStreak={stats.artistLongestStreak} />
      </FadeSection>
      <FadeSection>
        <AlbumCompletion albumCompletions={stats.albumCompletions} />
      </FadeSection>
      <FadeSection>
        <ListeningPreferences
          durationPreference={stats.durationPreference}
          explicitPreference={stats.explicitPreference}
        />
      </FadeSection>
      <FadeSection>
        <PopularityDistribution
          popularityDistribution={stats.popularityDistribution}
        />
      </FadeSection>
      <div className="h-16"></div> {/* Added gap */}
      <FadeSection>
        <WeeklyPattern dayDistribution={stats.dayDistribution} />
      </FadeSection>
      <FadeSection>
        <ListeningSessions sessionTypes={stats.sessionTypes} />
      </FadeSection>
      <FadeSection>
        <GenreDistribution />
      </FadeSection>
      <FadeSection>
        <ReleaseYearDistribution
          releaseYearDistribution={stats.releaseYearDistribution}
        />
      </FadeSection>
    </div>
  );
}
