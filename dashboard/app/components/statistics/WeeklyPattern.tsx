"use client";

import { motion } from "framer-motion";
import CountUp from "react-countup";
import { DayDistribution } from "../../types/stats";

interface WeeklyPatternProps {
  dayDistribution: DayDistribution[];
}

export default function WeeklyPattern({ dayDistribution }: WeeklyPatternProps) {
  // Find the day with most plays
  const busyDay = [...dayDistribution].sort(
    (a, b) => b.playCount - a.playCount
  )[0];

  // Find average variety percentages
  const avgSongVariety =
    dayDistribution.reduce((sum, day) => sum + day.songVarietyPercentage, 0) /
    7;
  const avgArtistVariety =
    dayDistribution.reduce((sum, day) => sum + day.artistVarietyPercentage, 0) /
    7;

  const getWeekendWarrior = () => {
    const weekendPlays = dayDistribution
      .filter((day) => ["Saturday", "Sunday"].includes(day.dayOfWeek))
      .reduce((sum, day) => sum + day.playCount, 0);

    const weekdayPlays =
      dayDistribution
        .filter((day) => !["Saturday", "Sunday"].includes(day.dayOfWeek))
        .reduce((sum, day) => sum + day.playCount, 0) / 5; // average weekday

    return weekendPlays / 2 > weekdayPlays * 1.5; // 50% more on weekends
  };

  const getListenerType = () => {
    if (avgSongVariety > 80) return "The Adventurous Soul ";
    if (avgArtistVariety > 80) return "The Artist Explorer ";
    if (getWeekendWarrior()) return "The Weekend Warrior ";
    if (busyDay.dayOfWeek === "Monday") return "The Monday Motivator ";
    if (busyDay.dayOfWeek === "Friday") return "The Friday Raver ";
    return "The Steady Groover 🎵";
  };

  const getListenerDescription = () => {
    if (avgSongVariety > 80) {
      return "You're all about that variety! Your playlist is like a box of chocolates - never know what you're gonna get next! ";
    }
    if (avgArtistVariety > 80) {
      return "You're on a mission to discover every artist out there! Your music library is like a who's who of the music world ";
    }
    if (getWeekendWarrior()) {
      return "When the weekend hits, so does your playlist! You're living for those Saturday and Sunday vibes ";
    }
    if (busyDay.dayOfWeek === "Monday") {
      return "Starting the week strong! Nothing beats those Monday motivation tunes, right? ";
    }
    if (busyDay.dayOfWeek === "Friday") {
      return "TGIF is your motto! You're bringing the weekend energy with your Friday playlist ";
    }
    return "You keep it steady and groovy all week long. Consistency is your middle name! ";
  };

  const getDayMood = (day: string, playCount: number) => {
    const maxPlays = Math.max(...dayDistribution.map((d) => d.playCount));
    const intensity = playCount / maxPlays;

    switch (day) {
      case "Monday":
        return intensity > 0.8
          ? "Monday Motivation on max! "
          : "Case of the Mondays? ";
      case "Tuesday":
        return intensity > 0.8
          ? "Taco Tuesday energy! "
          : "Just another Tuesday... ";
      case "Wednesday":
        return intensity > 0.8 ? "Wednesday warrior! " : "Hump daaaaay ";
      case "Thursday":
        return intensity > 0.8
          ? "Thursday's looking good! "
          : "Almost Friday... ";
      case "Friday":
        return intensity > 0.8
          ? "Friday mode: ACTIVATED! "
          : "TGIF (barely) 😮";
      case "Saturday":
        return intensity > 0.8 ? "Weekend goes BRRRR! " : "Lazy Saturday? ";
      case "Sunday":
        return intensity > 0.8 ? "Sunday funday! " : "Sunday scaries? ";
      default:
        return "";
    }
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
          <h2 className="text-3xl font-bold">Your Week in Beats </h2>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 1.5, delay: 0.5 }}
          >
            <p className="text-gray-400 max-w-2xl mx-auto">
              Let's see how your music vibes flow through the week...
            </p>
          </motion.div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 1.5, delay: 0.5 }}
        >
          <div className="grid gap-4">
            {dayDistribution.map((day, index) => (
              <motion.div
                key={index}
                className="bg-white/5 p-6 rounded-lg"
                initial={{ opacity: 0, x: -20 }}
                whileInView={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
              >
                <div className="flex justify-between items-center mb-4">
                  <div>
                    <h3 className="text-xl font-bold">{day.dayOfWeek}</h3>
                    <p className="text-sm text-gray-500">
                      {getDayMood(day.dayOfWeek, day.playCount)}
                    </p>
                  </div>
                  <span className="text-2xl font-bold text-green-400">
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
                        whileInView={{ width: `${day.songVarietyPercentage}%` }}
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
        </motion.div>

        <motion.div
          className="text-center space-y-4"
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          transition={{ duration: 0.5 }}
        >
          <div className="bg-white/5 p-6 rounded-lg mt-4">
            <h3 className="text-xl font-bold mb-2">{getListenerType()}</h3>
            <p className="text-gray-400 text-sm mb-4">
              {getListenerDescription()}
            </p>
            <div className="flex justify-between text-sm text-gray-500">
              <span>Song Variety: {avgSongVariety.toFixed(1)}%</span>
              <span>Artist Variety: {avgArtistVariety.toFixed(1)}%</span>
            </div>
          </div>
        </motion.div>
      </div>
    </motion.div>
  );
}
