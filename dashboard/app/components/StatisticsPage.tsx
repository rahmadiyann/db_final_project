"use client";

import { motion, useScroll } from "framer-motion";
import CountUp from "react-countup";
import { useRef } from "react";
import { ListeningStats } from "../types/stats";
import { Line, Doughnut } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
} from "chart.js";

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
);

interface StatisticsPageProps {
  stats: ListeningStats;
}

function formatDate(dateString: string) {
  return new Date(dateString).toLocaleDateString("en-US", {
    weekday: "long",
    year: "numeric",
    month: "long",
    day: "numeric",
  });
}

export default function StatisticsPage({ stats }: StatisticsPageProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ["start start", "end end"],
  });

  const formattedStartDate = formatDate(stats.artistLongestStreak.dateFrom);
  const formattedEndDate = formatDate(stats.artistLongestStreak.dateUntil);
  const formattedLongestDay = formatDate(stats.longestListeningDay.date);

  const sections = [
    // Section 1: Overview
    {
      component: (
        <motion.div
          className="min-h-screen flex items-center justify-center"
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
        >
          <div className="text-center space-y-8">
            <h1 className="text-4xl md:text-6xl font-bold">
              You listened to{" "}
              <motion.span className="text-green-400">
                <CountUp
                  end={stats.totalMinutesListened}
                  duration={2.5}
                  separator=","
                />{" "}
                minutes
              </motion.span>{" "}
              of music
            </h1>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 1 }}
              className="text-2xl text-purple-400"
            >
              That's like {(stats.totalMinutesListened / 1440).toFixed(1)} days
              of non-stop music!
            </motion.div>
          </div>
        </motion.div>
      ),
    },

    // Section 2: Daily Rhythm
    {
      component: (
        <motion.div
          className="min-h-screen flex items-center justify-center"
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
        >
          <div className="space-y-6 w-full max-w-4xl px-4">
            <h2 className="text-3xl font-bold text-center mb-8">
              Your Daily Rhythm
            </h2>
            <div className="h-64 bg-black/20 rounded-lg p-4">
              <Line
                data={{
                  labels: stats.hourDistribution.map(
                    (h) => `${h.hourOfDay}:00`
                  ),
                  datasets: [
                    {
                      label: "Listening Activity",
                      data: stats.hourDistribution.map((h) => h.percentage),
                      borderColor: "rgb(129, 140, 248)",
                      tension: 0.4,
                      fill: true,
                      backgroundColor: "rgba(129, 140, 248, 0.1)",
                    },
                  ],
                }}
                options={{
                  responsive: true,
                  maintainAspectRatio: false,
                  scales: {
                    y: {
                      beginAtZero: true,
                      grid: {
                        color: "rgba(255, 255, 255, 0.1)",
                      },
                    },
                    x: {
                      grid: {
                        color: "rgba(255, 255, 255, 0.1)",
                      },
                    },
                  },
                }}
              />
            </div>
          </div>
        </motion.div>
      ),
    },

    // Section 3: Artist Streak
    {
      component: (
        <motion.div
          className="min-h-screen flex items-center justify-center"
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
        >
          <div className="text-center space-y-6">
            <h2 className="text-3xl font-bold">Your Longest Artist Streak</h2>
            <div className="text-xl">
              You listened to{" "}
              <span className="text-pink-400 font-bold">
                {stats.artistLongestStreak.artistName}
              </span>{" "}
              for{" "}
              <motion.span
                initial={{ opacity: 0 }}
                whileInView={{ opacity: 1 }}
                viewport={{ once: true }}
                transition={{ delay: 0.5 }}
                className="text-yellow-400 font-bold"
              >
                <CountUp end={stats.artistLongestStreak.streak} duration={2} />{" "}
                days
              </motion.span>{" "}
              straight!
            </div>
            <div className="text-gray-400">
              From {formattedStartDate} to {formattedEndDate}
            </div>
          </div>
        </motion.div>
      ),
    },

    // Section 4: Album Completion
    {
      component: (
        <motion.div
          className="min-h-screen flex items-center justify-center"
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
        >
          <div className="space-y-8 w-full max-w-4xl px-4">
            <h2 className="text-3xl font-bold text-center">Album Deep Dives</h2>
            <div className="grid gap-4">
              {stats.albumCompletions.map((album, index) => (
                <motion.div
                  key={index}
                  className="bg-white/5 p-6 rounded-lg"
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                >
                  <div className="flex justify-between items-center mb-2">
                    <div>
                      <h3 className="text-xl font-bold">{album.albumTitle}</h3>
                      <p className="text-gray-400">{album.artistName}</p>
                    </div>
                    <span className="text-2xl font-bold text-green-400">
                      {album.completionPercentage}%
                    </span>
                  </div>
                  <div className="w-full bg-gray-700 rounded-full h-2">
                    <motion.div
                      className="bg-green-400 h-2 rounded-full"
                      initial={{ width: 0 }}
                      whileInView={{ width: `${album.completionPercentage}%` }}
                      transition={{ duration: 1 }}
                    />
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        </motion.div>
      ),
    },

    // Section 5: Listening Preferences
    {
      component: (
        <motion.div
          className="min-h-screen flex items-center justify-center"
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
        >
          <div className="space-y-12 w-full max-w-4xl px-4">
            <div>
              <h2 className="text-3xl font-bold text-center mb-8">
                Your Song Length Sweet Spot
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {stats.durationPreference.map((pref, index) => (
                  <motion.div
                    key={index}
                    className="bg-white/5 p-4 rounded-lg text-center"
                    initial={{ opacity: 0, scale: 0.9 }}
                    whileInView={{ opacity: 1, scale: 1 }}
                    transition={{ delay: index * 0.2 }}
                  >
                    <div className="text-4xl font-bold text-blue-400 mb-2">
                      {pref.percentage}%
                    </div>
                    <div className="text-gray-400">{pref.category}</div>
                  </motion.div>
                ))}
              </div>
            </div>

            <div>
              <h2 className="text-3xl font-bold text-center mb-8">
                Content Rating Preference
              </h2>
              <div className="grid grid-cols-2 gap-4">
                {stats.explicitPreference.map((pref, index) => (
                  <motion.div
                    key={index}
                    className="bg-white/5 p-6 rounded-lg text-center"
                    initial={{ opacity: 0, x: index === 0 ? -20 : 20 }}
                    whileInView={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.3 }}
                  >
                    <div className="text-4xl font-bold mb-2">
                      <CountUp end={pref.percentage} duration={2} />%
                    </div>
                    <div className="text-gray-400">
                      {pref.explicit ? "Explicit" : "Clean"}
                    </div>
                  </motion.div>
                ))}
              </div>
            </div>
          </div>
        </motion.div>
      ),
    },

    // Section 6: Song Popularity
    {
      component: (
        <motion.div
          className="min-h-screen flex items-center justify-center"
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
        >
          <div className="space-y-8 w-full max-w-4xl px-4">
            <h2 className="text-3xl font-bold text-center">
              Your Music Discovery Pattern
            </h2>
            <div className="grid gap-3">
              {stats.popularityDistribution.map((pop, index) => (
                <motion.div
                  key={index}
                  className="bg-white/5 p-4 rounded-lg"
                  initial={{ opacity: 0, x: -20 }}
                  whileInView={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                >
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-gray-400">
                      Popularity {pop.popularityRange}
                    </span>
                    <span className="font-bold">{pop.percentage}%</span>
                  </div>
                  <div className="w-full bg-gray-700 rounded-full h-2">
                    <motion.div
                      className="bg-purple-400 h-2 rounded-full"
                      initial={{ width: 0 }}
                      whileInView={{ width: `${pop.percentage}%` }}
                      transition={{ duration: 1 }}
                    />
                  </div>
                </motion.div>
              ))}
            </div>
            <p className="text-center text-gray-400">
              {
                stats.popularityDistribution.find(
                  (p) =>
                    p.percentage ===
                    Math.max(
                      ...stats.popularityDistribution.map((p) => p.percentage)
                    )
                )?.popularityRange
              }{" "}
              popularity songs are your sweet spot!
            </p>
          </div>
        </motion.div>
      ),
    },

    // Section 7: Release Years
    {
      component: (
        <motion.div
          className="min-h-screen flex items-center justify-center"
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
        >
          <div className="space-y-8 w-full max-w-4xl px-4">
            <h2 className="text-3xl font-bold text-center">
              Your Music Timeline
            </h2>
            <div className="h-64">
              <Line
                data={{
                  labels: stats.releaseYearDistribution.map((d) =>
                    d.year.toString()
                  ),
                  datasets: [
                    {
                      label: "Plays by Release Year",
                      data: stats.releaseYearDistribution.map(
                        (d) => d.playCount
                      ),
                      borderColor: "rgb(234, 179, 8)",
                      backgroundColor: "rgba(234, 179, 8, 0.1)",
                      fill: true,
                      tension: 0.4,
                    },
                  ],
                }}
                options={{
                  responsive: true,
                  maintainAspectRatio: false,
                  scales: {
                    y: {
                      beginAtZero: true,
                      grid: {
                        color: "rgba(255, 255, 255, 0.1)",
                      },
                    },
                    x: {
                      grid: {
                        color: "rgba(255, 255, 255, 0.1)",
                      },
                    },
                  },
                }}
              />
            </div>
          </div>
        </motion.div>
      ),
    },

    // Section 8: Weekly Listening Patterns
    {
      component: (
        <motion.div
          className="min-h-screen flex items-center justify-center"
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
        >
          <div className="space-y-8 w-full max-w-4xl px-4">
            <h2 className="text-3xl font-bold text-center">
              Your Weekly Rhythm
            </h2>
            <div className="grid gap-4">
              {stats.dayDistribution.map((day, index) => (
                <motion.div
                  key={index}
                  className="bg-white/5 p-6 rounded-lg"
                  initial={{ opacity: 0, x: -20 }}
                  whileInView={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                >
                  <div className="flex justify-between items-center mb-4">
                    <h3 className="text-xl font-bold">{day.dayOfWeek}</h3>
                    <span className="text-green-400">
                      <CountUp end={day.playCount} duration={2} /> plays
                    </span>
                  </div>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <div className="text-gray-400 mb-1">Song Variety</div>
                      <div className="w-full bg-gray-700 rounded-full h-2">
                        <motion.div
                          className="bg-blue-400 h-2 rounded-full"
                          initial={{ width: 0 }}
                          whileInView={{
                            width: `${day.songVarietyPercentage}%`,
                          }}
                          transition={{ duration: 1 }}
                        />
                      </div>
                    </div>
                    <div>
                      <div className="text-gray-400 mb-1">Artist Variety</div>
                      <div className="w-full bg-gray-700 rounded-full h-2">
                        <motion.div
                          className="bg-purple-400 h-2 rounded-full"
                          initial={{ width: 0 }}
                          whileInView={{
                            width: `${day.artistVarietyPercentage}%`,
                          }}
                          transition={{ duration: 1 }}
                        />
                      </div>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        </motion.div>
      ),
    },

    // Section 9: Listening Sessions
    {
      component: (
        <motion.div
          className="min-h-screen flex items-center justify-center"
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
        >
          <div className="space-y-8 w-full max-w-4xl px-4">
            <h2 className="text-3xl font-bold text-center">
              Your Listening Sessions
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {stats.sessionTypes.map((session, index) => (
                <motion.div
                  key={index}
                  className="bg-white/5 p-6 rounded-lg"
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.2 }}
                >
                  <div className="text-2xl font-bold mb-2">
                    {session.sessionType}
                  </div>
                  <div className="text-4xl font-bold text-indigo-400 mb-2">
                    <CountUp end={session.percentage} duration={2} />%
                  </div>
                  <div className="text-gray-400">
                    <CountUp end={session.count} duration={2} /> times
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        </motion.div>
      ),
    },

    // Section 10: Longest Listening Day
    {
      component: (
        <motion.div
          className="min-h-screen flex items-center justify-center"
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
        >
          <div className="text-center space-y-6">
            <h2 className="text-3xl font-bold">Your Most Active Day</h2>
            <div className="text-6xl font-bold text-yellow-400">
              <CountUp
                end={stats.longestListeningDay.playCount}
                duration={2.5}
              />
            </div>
            <div className="text-xl">songs played on {formattedLongestDay}</div>
            <motion.div
              className="text-gray-400"
              initial={{ opacity: 0 }}
              whileInView={{ opacity: 1 }}
              transition={{ delay: 1 }}
            >
              That's an average of{" "}
              {(stats.longestListeningDay.playCount / 24).toFixed(1)} songs per
              hour!
            </motion.div>
          </div>
        </motion.div>
      ),
    },

    // Section 11: Genre Distribution
    {
      component: (
        <motion.div
          className="min-h-screen flex items-center justify-center"
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
        >
          <div className="space-y-8 w-full max-w-4xl px-4">
            <h2 className="text-3xl font-bold text-center">
              Genre Distribution
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              <div className="aspect-square">
                <Doughnut
                  data={{
                    labels: ["Pop", "Hip-Hop", "Rock", "Electronic", "Other"],
                    datasets: [
                      {
                        data: [30, 25, 20, 15, 10],
                        backgroundColor: [
                          "rgba(255, 99, 132, 0.8)",
                          "rgba(54, 162, 235, 0.8)",
                          "rgba(255, 206, 86, 0.8)",
                          "rgba(75, 192, 192, 0.8)",
                          "rgba(153, 102, 255, 0.8)",
                        ],
                      },
                    ],
                  }}
                  options={{
                    plugins: {
                      legend: {
                        position: "right",
                      },
                    },
                  }}
                />
              </div>
              <div className="flex items-center">
                <div className="space-y-4">
                  <h3 className="text-xl font-bold">Your Top Genre</h3>
                  <p className="text-gray-400">
                    Pop music dominates your listening habits, making up 30% of
                    your total plays. You're most likely to listen to pop music
                    during weekday afternoons.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </motion.div>
      ),
    },
  ];

  return (
    <div ref={containerRef} className="bg-black text-white">
      {sections.map((section, index) => (
        <div key={index} className="snap-start">
          {section.component}
        </div>
      ))}
    </div>
  );
}
