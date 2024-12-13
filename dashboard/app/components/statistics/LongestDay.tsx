"use client";

import { motion } from "framer-motion";
import CountUp from "react-countup";
import { LongestDay as LongestDayType } from "../../types/stats";
import { formatDate } from "../../utils/dateFormatters";

interface LongestDayProps {
  longestListeningDay: LongestDayType;
}

export default function LongestDay({ longestListeningDay }: LongestDayProps) {
  const formattedDate = formatDate(longestListeningDay.date);
  const songsPerHour = longestListeningDay.playCount / 24;
  const songsPerMinute = songsPerHour / 60;

  const getListenerMood = () => {
    if (longestListeningDay.playCount > 300) return "You listened to";
    if (longestListeningDay.playCount > 200) return "You listened to";
    if (longestListeningDay.playCount > 100) return "You listened to";
    return "Solid Music Day! ";
  };

  const getFunFact = () => {
    const minutes = Math.round(3 * longestListeningDay.playCount); // Assuming avg song is 3 mins
    const hours = Math.round(minutes / 60);

    if (hours > 16) {
      return "Did you even sleep that day?  That's more music than there are hours in the day!";
    }
    if (hours > 12) {
      return "That's like having music as your full-time job!  (Best job ever?)";
    }
    if (hours > 8) {
      return "You spent more time with music than most people spend at work! ";
    }
    return "How do you even have the time? ";
  };

  const getTimeComparison = () => {
    const totalMinutes = 3 * longestListeningDay.playCount; // Assuming avg song is 3 mins

    // Fun comparisons
    const coffeesDrunk = Math.round(totalMinutes / 15); // Time to drink a coffee
    const moviesWatched = (totalMinutes / 120).toFixed(1); // Avg movie length
    const flightsToMoon = (totalMinutes / 240).toFixed(1); // Time to watch Apollo 13

    return {
      coffees: coffeesDrunk,
      movies: moviesWatched,
      flights: flightsToMoon,
    };
  };

  const comparisons = getTimeComparison();

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
          <h2 className="text-3xl font-bold">Your Musical Marathon </h2>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 1.5, delay: 0.5 }}
          >
            <p className="text-gray-400 max-w-2xl mx-auto">
              Everyone has that one day when they just can't stop the music...
            </p>
          </motion.div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 1.5, delay: 0.5 }}
        >
          <div className="bg-white/5 p-6 rounded-lg mt-4">
            <h3 className="text-xl font-bold mb-4">{getListenerMood()}</h3>
            <div className="text-6xl font-bold text-yellow-400 mb-4">
              <CountUp end={longestListeningDay.playCount} duration={2.5} />
            </div>
            <div className="text-xl mb-2">songs on {formattedDate}</div>
            <p className="text-gray-400 text-sm">{getFunFact()}</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-8">
            <motion.div
              className="bg-white/5 p-6 rounded-lg"
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
            >
              <div className="text-2xl font-bold text-blue-400">
                <CountUp end={songsPerHour} duration={2} decimals={1} />
              </div>
              <div className="text-gray-400">songs per hour</div>
              <div className="text-sm text-gray-500 mt-2">
                Never a quiet moment!
              </div>
            </motion.div>

            <motion.div
              className="bg-white/5 p-6 rounded-lg"
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
            >
              <div className="text-2xl font-bold text-green-400">
                {comparisons.movies}
              </div>
              <div className="text-gray-400">movies worth of music</div>
              <div className="text-sm text-gray-500 mt-2">
                Who needs Netflix?
              </div>
            </motion.div>

            <motion.div
              className="bg-white/5 p-6 rounded-lg"
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
            >
              <div className="text-2xl font-bold text-purple-400">
                {comparisons.coffees}
              </div>
              <div className="text-gray-400">coffees worth of time</div>
              <div className="text-sm text-gray-500 mt-2">
                Caffeine who? Music is your energy! ☕
              </div>
            </motion.div>
          </div>

          <motion.div
            className="bg-white/5 p-6 rounded-lg mt-4"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
          >
            <h3 className="text-xl font-semibold mb-2">
              {songsPerMinute >= 1
                ? "You averaged more than one song per minute! Talk about speed listening! "
                : "That's like having a personal DJ for your entire day! "}
            </h3>
          </motion.div>
        </motion.div>
      </div>
    </motion.div>
  );
}
