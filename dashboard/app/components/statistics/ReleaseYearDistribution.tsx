"use client";

import { motion } from "framer-motion";
import { Line } from "react-chartjs-2";
import { ReleaseYearDistribution as ReleaseYearType } from "../../types/stats";
import { commonChartOptions } from "../../utils/chartConfig";
import CountUp from "react-countup";
import { TooltipItem } from "chart.js";

interface ReleaseYearDistributionProps {
  releaseYearDistribution: ReleaseYearType[];
}

export default function ReleaseYearDistribution({
  releaseYearDistribution,
}: ReleaseYearDistributionProps) {
  // Find peak year and calculate averages
  const peakYear = [...releaseYearDistribution].sort(
    (a, b) => b.playCount - a.playCount
  )[0];

  const avgYear =
    releaseYearDistribution.reduce(
      (sum, year) => sum + year.year * year.playCount,
      0
    ) / releaseYearDistribution.reduce((sum, year) => sum + year.playCount, 0);

  const currentYear = new Date().getFullYear();
  const musicAge = currentYear - avgYear;

  const getListenerType = () => {
    if (peakYear.year >= currentYear - 2) return "The Trendsetter ";
    if (peakYear.year >= currentYear - 5) return "The Modern Classic ";
    if (peakYear.year >= 2000) return "The Millennial Maestro ";
    if (peakYear.year >= 1990) return "The 90s Nostalgic ";
    if (peakYear.year >= 1980) return "The Retro Enthusiast ";
    return "The Vintage Virtuoso 🎻";
  };

  const getListenerDescription = () => {
    if (peakYear.year >= currentYear - 2) {
      return "Fresh off the press! You're always first in line for the latest releases. The ink's barely dry on these tracks! ";
    }
    if (peakYear.year >= currentYear - 5) {
      return "You've got a sweet spot for recent classics. Not too new, not too old - just right! ";
    }
    if (peakYear.year >= 2000) {
      return "Y2K bug? More like Y2K groove! The millennium's greatest hits are your jam! ";
    }
    if (peakYear.year >= 1990) {
      return "90s kid at heart! When the beat drops, you're transported back to the golden age! ";
    }
    if (peakYear.year >= 1980) {
      return "Keeping the 80s alive! Big hair, bigger sounds - that's your style! ";
    }
    return "They don't make 'em like they used to, right? You're keeping the classics alive! ";
  };

  const getTimeMachine = () => {
    const decade = Math.floor(avgYear / 10) * 10;
    switch (decade) {
      case 2020:
        return "living in the future! ";
      case 2010:
        return "vibing with the 2010s! ";
      case 2000:
        return "partying like it's Y2K! ";
      case 1990:
        return "keeping the 90s alive! ";
      case 1980:
        return "stuck in the 80s... in a good way! ";
      case 1970:
        return "grooving with the 70s! ";
      default:
        return "on a timeless journey! ";
    }
  };

  // Sort the distribution by year ascending
  const sortedDistribution = [...releaseYearDistribution].sort(
    (a, b) => a.year - b.year
  );

  const chartData = {
    labels: sortedDistribution.map((d) => d.year.toString()),
    datasets: [
      {
        label: "Plays by Release Year",
        data: sortedDistribution.map((d) => d.playCount),
        borderColor: "rgb(234, 179, 8)",
        backgroundColor: "rgba(234, 179, 8, 0.3)",
        fill: true,
        tension: 0.4,
        pointBackgroundColor: "rgb(234, 179, 8)",
        pointBorderColor: "rgba(255, 255, 255, 0.7)",
        pointHoverRadius: 8,
        pointHoverBackgroundColor: "rgba(255, 255, 255, 0.9)",
        pointHoverBorderColor: "rgb(234, 179, 8)",
        pointRadius: 5,
      },
    ],
  };

  const customChartOptions = {
    ...commonChartOptions,
    plugins: {
      legend: {
        display: true,
        position: "top" as const,
        align: "start" as const,
        labels: {
          color: "rgba(255, 255, 255, 0.7)",
          usePointStyle: true,
          boxWidth: 10,
        },
      },
      tooltip: {
        enabled: true,
        backgroundColor: "rgba(0, 0, 0, 0.7)",
        titleColor: "rgba(255, 255, 255, 0.9)",
        bodyColor: "rgba(255, 255, 255, 0.9)",
        borderColor: "rgb(234, 179, 8)",
        borderWidth: 1,
        callbacks: {
          label: function (context: TooltipItem<"line">) {
            return `Year: ${context.label}, Plays: ${context.raw}`;
          },
        },
      },
    },
    scales: {
      x: {
        title: {
          display: true,
          text: "Release Year",
          color: "rgba(255, 255, 255, 0.7)",
        },
        ticks: {
          color: "rgba(255, 255, 255, 0.7)",
        },
        grid: { color: "rgba(255, 255, 255, 0.1)" },
      },
      y: {
        title: {
          display: true,
          text: "Play Count",
          color: "rgba(255, 255, 255, 0.7)",
        },
        ticks: {
          color: "rgba(255, 255, 255, 0.7)",
        },
        grid: { color: "rgba(255, 255, 255, 0.1)" },
      },
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
        >
          <h2 className="text-3xl font-bold">Your Time Machine </h2>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 1.5, delay: 0.5 }}
          >
            <p className="text-gray-400 max-w-2xl mx-auto">
              From vintage vinyl to digital drops...
            </p>
          </motion.div>
        </motion.div>

        <motion.div
          className="bg-white/5 p-6 rounded-lg mt-4"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
        >
          <h3 className="text-xl font-bold mb-2">{getListenerType()}</h3>
          <p className="text-gray-400 text-sm mb-4">
            {getListenerDescription()}
          </p>
          <div className="grid grid-cols-3 gap-4 text-sm text-gray-500">
            <div>
              <div className="text-yellow-400 font-bold">
                <CountUp end={peakYear.year} duration={2} separator="" />
              </div>
              <div>Peak Year 🏆</div>
            </div>
            <div>
              <div className="text-orange-400 font-bold">
                <CountUp end={avgYear} duration={2} decimals={1} separator="" />
              </div>
              <div>Average Year 📊</div>
            </div>
            <div>
              <div className="text-pink-400 font-bold">
                <CountUp end={musicAge} duration={2} decimals={1} />
              </div>
              <div>Music Age 🎧</div>
            </div>
          </div>
        </motion.div>

        <div className="bg-black/20 rounded-lg p-6">
          <div className="h-64">
            <Line data={chartData} options={customChartOptions} />
          </div>
        </div>

        <motion.div
          className="bg-white/5 p-6 rounded-lg"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
        >
          <h3 className="text-xl font-semibold mb-2">Time Travel Report </h3>
          <p className="text-gray-400">
            On average, your musical time machine is {getTimeMachine()} Your
            playlist is like a journey through{" "}
            <span className="text-yellow-400">
              {Math.round(musicAge * 10) / 10}
            </span>{" "}
            years of music history!
          </p>
        </motion.div>
      </div>
    </motion.div>
  );
}
