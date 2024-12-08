"use client";

import { motion } from "framer-motion";
import { PolarArea } from "react-chartjs-2";
import { commonChartOptions } from "../../utils/chartConfig";
import {
  Chart as ChartJS,
  RadialLinearScale,
  ArcElement,
  Tooltip,
  Legend,
} from "chart.js";

ChartJS.register(RadialLinearScale, ArcElement, Tooltip, Legend);

interface Genre {
  name: string;
  percentage: number;
  color: string;
  emoji: string;
  description: string;
}

export default function GenreDistribution() {
  const genres: Genre[] = [
    {
      name: "Pop",
      percentage: 23.7,
      color: "rgba(255, 99, 132, 0.8)",
      emoji: "🎵",
      description: "Chart-toppers and catchy tunes",
    },
    {
      name: "Hip-Hop",
      percentage: 18.4,
      color: "rgba(54, 162, 235, 0.8)",
      emoji: "🎤",
      description: "Beats and rhymes",
    },
    {
      name: "Rock",
      percentage: 15.9,
      color: "rgba(255, 206, 86, 0.8)",
      emoji: "🎸",
      description: "Guitar-driven classics",
    },
    {
      name: "Electronic",
      percentage: 12.3,
      color: "rgba(75, 192, 192, 0.8)",
      emoji: "💫",
      description: "Digital soundscapes",
    },
    {
      name: "R&B",
      percentage: 8.7,
      color: "rgba(153, 102, 255, 0.8)",
      emoji: "🎶",
      description: "Smooth grooves and soul",
    },
    {
      name: "Jazz",
      percentage: 6.4,
      color: "rgba(255, 159, 64, 0.8)",
      emoji: "🎷",
      description: "Improvisational masterpieces",
    },
    {
      name: "Classical",
      percentage: 5.2,
      color: "rgba(201, 203, 207, 0.8)",
      emoji: "🎻",
      description: "Timeless orchestral works",
    },
    {
      name: "Metal",
      percentage: 4.8,
      color: "rgba(100, 100, 100, 0.8)",
      emoji: "🤘",
      description: "Heavy riffs and intensity",
    },
    {
      name: "Other",
      percentage: 4.6,
      color: "rgba(153, 102, 255, 0.8)",
      emoji: "✨",
      description: "Genre-bending gems",
    },
  ];

  const dominantGenre = genres.reduce(
    (max, genre) => (genre.percentage > max.percentage ? genre : max),
    genres[0]
  );

  const chartData = {
    labels: genres.map((genre) => `${genre.emoji} ${genre.name}`),
    datasets: [
      {
        data: genres.map((genre) => genre.percentage),
        backgroundColor: genres.map((genre) => genre.color),
        borderColor: genres.map(() => "rgba(255, 255, 255, 0.8)"),
        borderWidth: 1,
      },
    ],
  };

  const customChartOptions = {
    ...commonChartOptions,
    plugins: {
      ...commonChartOptions.plugins,
      legend: {
        position: "right" as const,
        labels: {
          font: {
            size: 14,
            family: "'Helvetica Neue', 'Helvetica', 'Arial', sans-serif",
            weight: "bold" as const,
          },
          color: "#ffffff",
          padding: 20,
        },
      },
    },
    scales: {
      r: {
        ticks: { display: false },
        grid: { color: "rgba(255, 255, 255, 0.1)" },
      },
    },
    animation: {
      animateScale: true,
      animateRotate: true,
      duration: 2000,
    },
  };

  return (
    <motion.div
      className="min-h-screen flex items-center justify-center"
      initial={{ opacity: 0 }}
      whileInView={{ opacity: 1 }}
      viewport={{ once: true }}
      transition={{ duration: 0.5 }}
    >
      <div className="space-y-8 w-full max-w-4xl px-4">
        <motion.div
          className="text-center space-y-4"
          initial={{ opacity: 1 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5 }}
        >
          <h2 className="text-3xl font-bold">Your Musical Palette 🎨</h2>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 1.5, delay: 0.5 }}
          >
            <p className="text-gray-400 max-w-2xl mx-auto">
              From beats to riffs, let's paint a picture of your musical taste!
              What colors your sonic world? 🌈
            </p>
          </motion.div>
        </motion.div>

        <motion.div
          className="grid grid-cols-1 md:grid-cols-1 gap-8"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 1.5, delay: 0.5 }}
        >
          <div className="aspect-square">
            <PolarArea data={chartData} options={customChartOptions} />
          </div>

          <div className="space-y-4">
            <motion.div
              className="bg-white/5 p-6 rounded-lg"
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5 }}
            >
              <h3 className="text-xl font-semibold mb-2">Fun Fact 🎈</h3>
              <p className="text-gray-400">
                {dominantGenre.percentage > 40
                  ? "You're a true genre loyalist! When you find your groove, you stick to it! 🎯"
                  : "You're keeping it diverse! Your playlist is like a music festival lineup! 🎪"}
              </p>
            </motion.div>
          </div>
        </motion.div>
      </div>
    </motion.div>
  );
}
