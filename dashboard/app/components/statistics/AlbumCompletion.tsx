"use client";

import { motion } from "framer-motion";
import { AlbumCompletion as AlbumCompletionType } from "../../types/stats";
import CountUp from "react-countup";
import Image from "next/image";

interface AlbumCompletionProps {
  albumCompletions: AlbumCompletionType[];
}

export default function AlbumCompletion({
  albumCompletions,
}: AlbumCompletionProps) {
  // Find completion stats
  const completedAlbums = albumCompletions.filter(
    (album) => album.completionPercentage === 100
  ).length;
  const inProgressAlbums = albumCompletions.filter(
    (album) =>
      album.completionPercentage > 0 && album.completionPercentage < 100
  ).length;
  const avgCompletion =
    albumCompletions.reduce(
      (sum, album) => sum + album.completionPercentage,
      0
    ) / albumCompletions.length;

  const getListenerType = () => {
    if (completedAlbums > albumCompletions.length * 0.7)
      return "The Completionist 🏆";
    if (avgCompletion > 75) return "The Album Enthusiast 💿";
    if (inProgressAlbums > albumCompletions.length * 0.8)
      return "The Explorer 🗺️";
    if (avgCompletion < 30) return "The Sampler 🎵";
    return "The Balanced Listener ⚖️";
  };

  const getListenerDescription = () => {
    if (completedAlbums > albumCompletions.length * 0.7) {
      return "You&apos;re not here to skip tracks! When you start an album, you&apos;re in it for the long haul. Artists love listeners like you! 🎸";
    }
    if (avgCompletion > 75) {
      return "You really appreciate the album format. Taking in the full artistic vision, one album at a time! 🎨";
    }
    if (inProgressAlbums > albumCompletions.length * 0.8) {
      return "So many albums, so little time! You&apos;re on a mission to explore every corner of your music library. 🚀";
    }
    if (avgCompletion < 30) {
      return "You know what you like! Why waste time when you&apos;ve found the perfect track? Hit that next button! ⏭️";
    }
    return "You&apos;ve got a healthy mix of full album deep-dives and quick hits. Keeping it interesting! 🎯";
  };

  const getCompletionMessage = (percentage: number) => {
    if (percentage === 100) return "Every track conquered! 👑";
    if (percentage > 75) return "Almost there! Keep going! 🎯";
    if (percentage > 50) return "Halfway through! 🌗";
    if (percentage > 25) return "Just getting started! 🌱";
    return "Time to explore! 🔍";
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
          <h2 className="text-3xl font-bold">Album Adventures 💿</h2>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 1.5, delay: 0.5 }}
          >
            <p className="text-gray-400 max-w-2xl mx-auto">
              Are you a track-skipper or an album purist? Let&apos;s see how
              thoroughly you explore your albums. No judgment... well, maybe a
              little! 😏
            </p>
          </motion.div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 1.5, delay: 0.5 }}
        >
          <div className="grid gap-4">
            {[...albumCompletions]
              .sort((a, b) => b.completionPercentage - a.completionPercentage)
              .map((album, index) => (
                <motion.div
                  key={index}
                  className="bg-white/5 p-6 rounded-lg relative overflow-hidden"
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                >
                  <div className="flex justify-between items-start mb-4">
                    <div className="flex gap-4">
                      <Image
                        src={album.albumImageUrl}
                        alt={`${album.albumTitle} cover`}
                        className="w-16 h-16 rounded-md object-cover"
                        width={64}
                        height={64}
                      />
                      <div>
                        <h3 className="text-xl font-bold">
                          {album.albumTitle}
                        </h3>
                        <p className="text-gray-400">{album.artistName}</p>
                        <p className="text-sm text-gray-500 mt-2">
                          {getCompletionMessage(album.completionPercentage)}
                        </p>
                      </div>
                    </div>
                    <div className="text-right">
                      <span className="text-2xl font-bold text-green-400">
                        <CountUp
                          end={album.completionPercentage}
                          duration={2}
                        />
                        %
                      </span>
                    </div>
                  </div>
                  <div className="flex justify-between text-xs text-white mb-1">
                    <div>{album.uniqueTracksPlayed}</div>
                    <div>{album.totalTracks}</div>
                  </div>
                  <div className="w-full bg-gray-700 rounded-full h-2 overflow-hidden relative">
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
          <div className="text-center space-y-4">
            <div className="bg-white/5 p-6 rounded-lg mt-4">
              <h3 className="text-xl font-bold mb-2">{getListenerType()}</h3>
              <p className="text-gray-400 text-sm mb-4">
                {getListenerDescription()}
              </p>
              <div className="grid grid-cols-3 gap-4 text-sm text-gray-500">
                <div>
                  <div className="text-green-400 font-bold">
                    <CountUp end={completedAlbums} duration={2} />
                  </div>
                  <div>Completed Albums</div>
                </div>
                <div>
                  <div className="text-yellow-400 font-bold">
                    <CountUp end={inProgressAlbums} duration={2} />
                  </div>
                  <div>In Progress</div>
                </div>
                <div>
                  <div className="text-blue-400 font-bold">
                    <CountUp end={avgCompletion} duration={2} decimals={1} />%
                  </div>
                  <div>Avg. Completion</div>
                </div>
              </div>
            </div>
          </div>
        </motion.div>
      </div>
    </motion.div>
  );
}
