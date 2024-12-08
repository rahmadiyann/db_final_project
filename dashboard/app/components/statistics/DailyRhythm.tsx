"use client";

import { motion } from "framer-motion";
import { Line } from "react-chartjs-2";
import { HourDistribution } from "../../types/stats";
import { commonChartOptions } from "../../utils/chartConfig";
import CountUp from "react-countup";

interface DailyRhythmProps {
  hourDistribution: HourDistribution[];
}

function formatHour(hour: number): string {
  const period = hour >= 12 ? "PM" : "AM";
  const displayHour = hour === 0 ? 12 : hour > 12 ? hour - 12 : hour;
  return `${displayHour}${period}`;
}

export default function DailyRhythm({ hourDistribution }: DailyRhythmProps) {
  // Sort hours chronologically
  const sortedDistribution = [...hourDistribution].sort(
    (a, b) => a.hourOfDay - b.hourOfDay
  );

  // Find peak listening hour
  const peakHour = sortedDistribution.reduce((max, current) =>
    current.percentage > max.percentage ? current : max
  );

  // Calculate time period distributions
  const morningHours = sortedDistribution
    .filter((h) => h.hourOfDay >= 5 && h.hourOfDay <= 11)
    .reduce((sum, h) => sum + h.percentage, 0);
  const afternoonHours = sortedDistribution
    .filter((h) => h.hourOfDay >= 12 && h.hourOfDay <= 17)
    .reduce((sum, h) => sum + h.percentage, 0);
  const eveningHours = sortedDistribution
    .filter((h) => h.hourOfDay >= 18 && h.hourOfDay <= 21)
    .reduce((sum, h) => sum + h.percentage, 0);
  const nightHours = sortedDistribution
    .filter((h) => h.hourOfDay >= 22 || h.hourOfDay <= 4)
    .reduce((sum, h) => sum + h.percentage, 0);

  const getListenerType = () => {
    if (nightHours > 35) return "The Night Owl 🦉";
    if (morningHours > 35) return "The Early Bird 🐦";
    if (afternoonHours > 35) return "The Midday Groover 🌞";
    if (eveningHours > 35) return "The Sunset Serenader 🌅";
    return "The All-Day DJ 🎧";
  };

  const getListenerDescription = () => {
    if (nightHours > 35) {
      return "When the world goes quiet, your playlist comes alive! The stars are your disco lights ✨";
    }
    if (morningHours > 35) {
      return "Rise and shine with the rhythm! Your day starts with the perfect soundtrack 🌅";
    }
    if (afternoonHours > 35) {
      return "Peak productivity hours? More like peak playlist hours! Keeping the midday energy high 🌞";
    }
    if (eveningHours > 35) {
      return "As the day winds down, your music winds up! Making every sunset a little more melodic 🎵";
    }
    return "Your music knows no time bounds - any hour is the right hour for the right tune! 🎪";
  };

  const getPeakHourMood = () => {
    const hour = peakHour.hourOfDay;
    if (hour >= 5 && hour <= 8) return "Early morning motivation! 💪";
    if (hour >= 9 && hour <= 11) return "Mid-morning groove! 🎵";
    if (hour >= 12 && hour <= 14) return "Lunch break beats! 🍽️";
    if (hour >= 15 && hour <= 17) return "Afternoon pick-me-up! ☕";
    if (hour >= 18 && hour <= 20) return "Evening vibes! 🌆";
    if (hour >= 21 && hour <= 23) return "Late night jams! 🌙";
    return "Midnight melodies! 🌠";
  };

  const chartData = {
    labels: sortedDistribution.map((h) => formatHour(h.hourOfDay)),
    datasets: [
      {
        label: "Listening Activity",
        data: sortedDistribution.map((h) => h.percentage),
        borderColor: "rgb(129, 140, 248)",
        tension: 0.4,
        fill: true,
        backgroundColor: "rgba(129, 140, 248, 0.1)",
      },
    ],
  };

  const customChartOptions = {
    ...commonChartOptions,
    plugins: {
      legend: {
        position: "top" as const,
        align: "end" as const,
        labels: {
          color: "rgba(255, 255, 255, 0.7)",
        },
      },
    },
    scales: {
      x: {
        ticks: {
          color: "rgba(255, 255, 255, 0.7)",
          maxRotation: 45,
          minRotation: 45,
        },
        grid: { color: "rgba(255, 255, 255, 0.1)" },
      },
      y: {
        beginAtZero: true,
        ticks: {
          color: "rgba(255, 255, 255, 0.7)",
          callback: function (tickValue: number | string) {
            return `${tickValue}%`;
          },
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
          <h2 className="text-3xl font-bold">Your Daily Rhythm 🎵</h2>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 1.5, delay: 0.5 }}
          >
            <p className="text-gray-400 max-w-2xl mx-auto">
              Every hour has its own soundtrack...
            </p>
          </motion.div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 1.5, delay: 0.5 }}
        >
          <div className="bg-black/20 rounded-lg p-6 mb-8">
            <div className="h-64">
              <Line data={chartData} options={customChartOptions} />
            </div>
          </div>

          <div className="text-center space-y-4 mb-8">
            <div className="bg-white/5 p-6 rounded-lg mt-4">
              <h3 className="text-xl font-bold mb-2">{getListenerType()}</h3>
              <p className="text-gray-400 text-sm mb-4">
                {getListenerDescription()}
              </p>
              <div className="grid grid-cols-4 gap-4 text-sm text-gray-500">
                <div>
                  <div className="text-yellow-400 font-bold">
                    <CountUp end={morningHours} duration={2} decimals={1} />%
                  </div>
                  <div>Morning Vibes 🌅</div>
                </div>
                <div>
                  <div className="text-orange-400 font-bold">
                    <CountUp end={afternoonHours} duration={2} decimals={1} />%
                  </div>
                  <div>Afternoon Groove 🌞</div>
                </div>
                <div>
                  <div className="text-pink-400 font-bold">
                    <CountUp end={eveningHours} duration={2} decimals={1} />%
                  </div>
                  <div>Evening Flow 🌆</div>
                </div>
                <div>
                  <div className="text-purple-400 font-bold">
                    <CountUp end={nightHours} duration={2} decimals={1} />%
                  </div>
                  <div>Night Mode 🌙</div>
                </div>
              </div>
            </div>
          </div>

          <div className="grid gap-6 md:grid-cols-2">
            <motion.div
              className="bg-white/5 p-6 rounded-lg mb-8"
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.2 }}
            >
              <h3 className="text-xl font-semibold mb-2">Peak Hour 🎧</h3>
              <p className="text-gray-400">
                <span className="text-indigo-400 font-bold">
                  {formatHour(peakHour.hourOfDay)}
                </span>{" "}
                is your power hour! {getPeakHourMood()}
                <br />
                <span className="text-sm">
                  That's when{" "}
                  <CountUp
                    end={peakHour.percentage}
                    duration={2}
                    decimals={1}
                    suffix="%"
                  />{" "}
                  of your listening happens.
                </span>
              </p>
            </motion.div>

            <motion.div
              className="bg-white/5 p-6 rounded-lg"
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.4 }}
            >
              <h3 className="text-xl font-semibold mb-2">Fun Fact 💫</h3>
              <p className="text-gray-400">
                {nightHours > morningHours
                  ? "You've spent more time vibing at night than during breakfast! Maybe that's why coffee was invented? ☕"
                  : "You're more likely to be jamming with your breakfast than your midnight snack! Early bird gets the bops! 🎵"}
              </p>
            </motion.div>
          </div>
        </motion.div>
      </div>
    </motion.div>
  );
}
