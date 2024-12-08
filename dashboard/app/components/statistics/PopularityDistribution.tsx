"use client";

import { motion } from "framer-motion";
import { PopularityDistribution as PopularityDistType } from "../../types/stats";
import CountUp from "react-countup";

interface PopularityDistributionProps {
  popularityDistribution: PopularityDistType[];
}

export default function PopularityDistribution({
  popularityDistribution,
}: PopularityDistributionProps) {
  // Find the highest percentage category
  const dominantCategory = [...popularityDistribution].sort(
    (a, b) => b.percentage - a.percentage
  )[0];

  // Calculate underground + rising vs popular + mainstream ratio
  const alternativeRatio = popularityDistribution
    .filter((p) => ["Underground", "Rising"].includes(p.popularityRange))
    .reduce((sum, p) => sum + (p.percentage || 0), 0);

  const mainstreamRatio = popularityDistribution
    .filter((p) => ["Popular", "Mainstream"].includes(p.popularityRange))
    .reduce((sum, p) => sum + (p.percentage || 0), 0);

  // Normalize ratios to ensure they add up to 100%
  const total = alternativeRatio + mainstreamRatio;
  const normalizedAlternative =
    total > 0 ? (alternativeRatio / total) * 100 : 0;
  const normalizedMainstream = total > 0 ? (mainstreamRatio / total) * 100 : 0;

  const getListenerType = () => {
    if (normalizedAlternative > 70) return "The Trendsetter 🎸";
    if (normalizedAlternative > 50) return "The Early Adopter 🔍";
    if (normalizedMainstream > 70) return "The Chart Chaser 📈";
    if (normalizedMainstream > 50) return "The Radio Lover 📻";
    return "The Balanced Explorer ⚖️";
  };

  const getListenerDescription = () => {
    if (normalizedAlternative > 70) {
      return "You're always ahead of the curve, discovering tomorrow's hits before they blow up. Your friends probably come to you for music recommendations!";
    }
    if (normalizedAlternative > 50) {
      return "You've got a knack for spotting rising talent, balancing underground gems with some mainstream hits. A true music explorer!";
    }
    if (normalizedMainstream > 70) {
      return "You're all about those chart-toppers! When a song's hot, you're right there vibing with the rest of the world.";
    }
    if (normalizedMainstream > 50) {
      return "You love keeping up with what's popular, but you're not afraid to venture into lesser-known territory occasionally.";
    }
    return "You're the perfect mix of mainstream and underground, equally comfortable with chart hits and hidden gems.";
  };

  const getMessage = (range: string) => {
    switch (range) {
      case "Underground":
        return "Hidden gems & indie treasures 💎";
      case "Rising":
        return "Tomorrow's hits, today 📈";
      case "Popular":
        return "Trending & buzzing tracks 🔥";
      case "Mainstream":
        return "Chart-toppers & radio favorites ⭐";
      default:
        return "";
    }
  };

  const getVerdict = (range: string) => {
    switch (range) {
      case "Underground":
        return "Ooh, we've got a hipster here! 🎸";
      case "Rising":
        return "Ahead of the curve, aren't we? 😎";
      case "Popular":
        return "Riding the wave of what's hot! 🌊";
      case "Mainstream":
        return "Living that billboard life! 🎯";
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
          <h2 className="text-3xl font-bold">Mainstream or Maverick? 🎵</h2>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 1.5, delay: 0.5 }}
          >
            <p className="text-gray-400 max-w-2xl mx-auto">
              Let&apos;s see where you stand in the popularity game...
            </p>
          </motion.div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 1.5, delay: 0.5 }}
        >
          <div className="grid gap-3">
            {popularityDistribution.map((pop, index) => (
              <motion.div
                key={index}
                className="bg-white/5 p-6 rounded-lg"
                initial={{ opacity: 0, x: -20 }}
                whileInView={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
              >
                <div className="flex justify-between items-center mb-2">
                  <div>
                    <span className="text-lg font-semibold text-gray-300">
                      {pop.popularityRange}
                    </span>
                    <p className="text-sm text-gray-500">
                      {getMessage(pop.popularityRange)}
                    </p>
                  </div>
                  <span className="text-2xl font-bold text-purple-400">
                    <CountUp end={pop.percentage} duration={2} />%
                  </span>
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
          <div className="text-center space-y-4">
            <div className="bg-white/5 p-4 rounded-lg inline-block mt-2">
              <p className="text-sm text-gray-400">
                The Verdict:{" "}
                <span className="text-purple-400 font-semibold">
                  {Math.round(dominantCategory.percentage)}%{" "}
                  {dominantCategory.popularityRange}
                </span>{" "}
                {getVerdict(dominantCategory.popularityRange)}
              </p>
            </div>
            <div className="bg-white/5 p-6 rounded-lg mt-4">
              <h3 className="text-xl font-bold mb-2">{getListenerType()}</h3>
              <p className="text-gray-400 text-sm mb-4">
                {getListenerDescription()}
              </p>
              <div className="flex justify-between text-sm text-gray-500">
                <span>
                  Alternative Vibes: {normalizedAlternative.toFixed(1)}%
                </span>
                <span>
                  Mainstream Energy: {normalizedMainstream.toFixed(1)}%
                </span>
              </div>
            </div>
          </div>
        </motion.div>
      </div>
    </motion.div>
  );
}
