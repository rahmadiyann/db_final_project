"use client";

import { motion } from "framer-motion";
import CountUp from "react-countup";

interface OverviewProps {
  totalMinutesListened: number;
}

export default function Overview({ totalMinutesListened }: OverviewProps) {
  const days = (totalMinutesListened / 1440).toFixed(1);
  const concerts = Math.round(totalMinutesListened / 90); // avg concert length 90 mins
  const albums = Math.round(totalMinutesListened / 45); // avg album length 45 mins

  const getFunFact = () => {
    if (totalMinutesListened > 100000) {
      return "You're basically living in headphones at this point! 🎧";
    }
    if (totalMinutesListened > 50000) {
      return "Your ears deserve a vacation! 🏖️";
    }
    if (totalMinutesListened > 20000) {
      return "That's some serious dedication! 🎵";
    }
    return "Now that's what we call a soundtrack to your month! 🎶";
  };

  return (
    <motion.div
      className="min-h-screen flex flex-col items-center justify-center relative"
      initial={{ opacity: 0 }}
      whileInView={{ opacity: 1 }}
      viewport={{ once: true }}
      transition={{ duration: 0.5 }}
    >
      <div className="text-center space-y-12">
        <motion.div
          className="space-y-4"
          initial={{ opacity: 1 }}
          animate={{ opacity: 1 }}
        >
          <h1 className="text-4xl md:text-6xl font-bold">
            This month, you spent
          </h1>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 1.5, delay: 0.5 }}
          >
            <div className="text-green-400 text-4xl md:text-6xl font-bold">
              <span className="inline-block min-w-[240px]">
                <CountUp
                  end={totalMinutesListened}
                  duration={2.5}
                  separator=","
                />
                {" minutes"}
              </span>
            </div>
            <div className="text-purple-400 text-3xl md:text-4xl font-medium">
              with music. Your ears deserve a medal.
            </div>
          </motion.div>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-4xl">
          <motion.div
            className="bg-white/5 p-6 rounded-lg"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 1 }}
          >
            <div className="text-3xl font-bold text-purple-400">
              {days} days
            </div>
            <div className="text-gray-400">of non-stop music</div>
          </motion.div>

          <motion.div
            className="bg-white/5 p-6 rounded-lg"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 1.2 }}
          >
            <div className="text-3xl font-bold text-blue-400">
              {concerts} concerts
            </div>
            <div className="text-gray-400">worth of music</div>
          </motion.div>

          <motion.div
            className="bg-white/5 p-6 rounded-lg"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 1.4 }}
          >
            <div className="text-3xl font-bold text-green-400">
              {albums} albums
            </div>
            <div className="text-gray-400">start to finish</div>
          </motion.div>
        </div>

        <motion.div
          className="text-xl text-gray-400 max-w-2xl"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1.8 }}
        >
          {getFunFact()}
        </motion.div>
      </div>

      <motion.div
        className="absolute bottom-12 text-center space-y-4"
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{
          duration: 1,
          delay: 2,
          repeat: Infinity,
          repeatType: "reverse",
        }}
      >
        <p className="text-gray-400 text-sm uppercase tracking-wider">
          Let's explore your musical journey ✨
        </p>
        <div className="flex justify-center">
          <motion.div
            className="w-5 h-8 border-2 border-gray-400 rounded-full p-1"
            initial={{ opacity: 0.5 }}
            animate={{ opacity: 1 }}
            transition={{
              duration: 1,
              repeat: Infinity,
              repeatType: "reverse",
            }}
          >
            <motion.div
              className="w-1 h-2 bg-gray-400 rounded-full mx-auto"
              animate={{ y: [0, 12, 0] }}
              transition={{
                duration: 1.5,
                repeat: Infinity,
                ease: "easeInOut",
              }}
            />
          </motion.div>
        </div>
      </motion.div>
    </motion.div>
  );
}
