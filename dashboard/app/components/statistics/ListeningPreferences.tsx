"use client";

import { motion } from "framer-motion";
import CountUp from "react-countup";
import { DurationPreference, ExplicitPreference } from "../../types/stats";

interface ListeningPreferencesProps {
  durationPreference: DurationPreference[];
  explicitPreference: ExplicitPreference[];
}

export default function ListeningPreferences({
  durationPreference,
  explicitPreference,
}: ListeningPreferencesProps) {
  // Find the duration preference with highest percentage
  const dominantDuration = [...durationPreference].sort(
    (a, b) => b.percentage - a.percentage
  )[0];

  // Calculate total explicit vs clean ratio
  const explicitRatio =
    explicitPreference.find((pref) => pref.explicit)?.percentage || 0;
  const cleanRatio =
    explicitPreference.find((pref) => !pref.explicit)?.percentage || 0;
  const preferredContent = explicitRatio > cleanRatio ? "explicit" : "clean";

  return (
    <motion.div
      className="min-h-screen flex items-center justify-center"
      initial={{ opacity: 0 }}
      whileInView={{ opacity: 1 }}
      viewport={{ once: true }}
      transition={{ duration: 0.5 }}
    >
      <div className="space-y-12 w-full max-w-4xl px-4">
        <motion.div
          className="text-center space-y-4"
          initial={{ opacity: 1 }}
          animate={{ opacity: 1 }}
        >
          <h2 className="text-3xl font-bold">
            I wonder, what kind of listener are you?
          </h2>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 1.5, delay: 0.5 }}
          >
            <p className="text-gray-400 max-w-2xl mx-auto">
              Let&apos;s see if you&apos;re a sprinter or a marathon runner when
              it comes to your tunes. Some like it quick, others like to take
              their sweet time... 😏
            </p>
          </motion.div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 1.5, delay: 0.5 }}
        >
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {["Short (&lt;3 min)", "Medium (3-5 min)", "Long (&gt;5 min)"].map(
              (category, index) => {
                const pref = durationPreference.find(
                  (p) => p.category === category
                );
                return (
                  <motion.div
                    key={index}
                    className="bg-white/5 p-6 rounded-lg text-center"
                    initial={{ opacity: 0, scale: 0.9 }}
                    whileInView={{ opacity: 1, scale: 1 }}
                    transition={{ delay: index * 0.2 }}
                  >
                    <div className="text-4xl font-bold text-blue-400 mb-2">
                      <CountUp end={pref?.percentage || 0} duration={2} />%
                    </div>
                    <div className="text-gray-400">{category}</div>
                    <div className="text-sm text-gray-500 mt-2">
                      {category === "Short (&lt;3 min)"
                        ? "For when you&apos;re feeling extra snippy ✂️"
                        : category === "Medium (3-5 min)"
                        ? "The Goldilocks zone - just right 👌"
                        : "For the musical adventurers 🗺️"}
                    </div>
                  </motion.div>
                );
              }
            )}
          </div>
          <div className="text-center space-y-4 mb-8">
            <div className="bg-white/5 p-4 rounded-lg inline-block mt-2">
              <p className="text-sm text-gray-400">
                The Verdict:{" "}
                <span className="text-blue-400 font-semibold">
                  {dominantDuration.category} tracks at{" "}
                  {dominantDuration.percentage}%
                </span>
                {dominantDuration.category === "Short (&lt; 3 min)" &&
                  " - Attention span of a goldfish, eh? 🐠"}
                {dominantDuration.category === "Medium (3-5 min)" &&
                  " - Playing it safe, aren&apos;t we? 😌"}
                {dominantDuration.category === "Long (&gt; 5 min)" &&
                  " - Someone&apos;s got commitment issues... to short songs! 🎸"}
              </p>
            </div>
          </div>
        </motion.div>

        <div>
          <div className="text-center space-y-4 mb-8">
            <h2 className="text-3xl font-bold">The Naughty or Nice List 😇</h2>
            <p className="text-gray-400 max-w-2xl mx-auto">
              Time to spill the tea on your content preferences! Let Let&apos;s
              see if you&apos;re keeping it PG or living life on the edge.
              Don&apos;t worry, we won&apos;t tell your mom... 🤫
            </p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {explicitPreference.map((pref, index) => (
              <motion.div
                key={index}
                className="bg-white/5 p-6 rounded-lg text-center relative overflow-hidden"
                initial={{ opacity: 0, x: index === 0 ? -20 : 20 }}
                whileInView={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.3 }}
              >
                <div className="relative z-10">
                  <div className="text-4xl font-bold mb-2">
                    <CountUp end={pref.percentage} duration={2} />%
                  </div>
                  <div className="text-gray-400 text-lg mb-1">
                    {pref.explicit ? "Explicit" : "Clean"}
                  </div>
                  <div className="text-sm text-gray-500">
                    {pref.explicit
                      ? "The spicier side of your library 🌶️"
                      : "Your mom-approved playlist 👌"}
                  </div>
                </div>
                <motion.div
                  className={`absolute bottom-0 left-0 h-1 ${
                    pref.explicit ? "bg-red-400" : "bg-green-400"
                  }`}
                  initial={{ width: 0 }}
                  whileInView={{ width: `${pref.percentage}%` }}
                  transition={{ duration: 1 }}
                />
              </motion.div>
            ))}
          </div>
          <div className="text-center space-y-4 mb-8">
            <div className="bg-white/5 p-4 rounded-lg inline-block mt-2">
              <p className="text-sm text-gray-400">
                {" "}
                <span
                  className={`font-semibold ${
                    preferredContent === "explicit"
                      ? "text-red-400"
                      : "text-green-400"
                  }`}
                >
                  {preferredContent === "explicit"
                    ? `${explicitRatio}% spicy content 🌶️`
                    : `${cleanRatio}% squeaky clean 😇`}
                </span>
                {preferredContent === "explicit"
                  ? " - Living life uncensored, you rebel! 😈"
                  : " - Your playlist would make your grandma proud! 👵"}
              </p>
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  );
}
