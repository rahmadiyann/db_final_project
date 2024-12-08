"use client";

import { motion } from "framer-motion";
import CountUp from "react-countup";
import { ArtistStreak as ArtistStreakType } from "../../types/stats";
import { formatDate } from "../../utils/dateFormatters";
import Image from "next/image";

interface ArtistStreakProps {
  artistStreak: ArtistStreakType;
}

export default function ArtistStreak({ artistStreak }: ArtistStreakProps) {
  const formattedStartDate = formatDate(artistStreak.dateFrom.toString());
  const formattedEndDate = formatDate(artistStreak.dateUntil.toString());

  return (
    <motion.div
      className="min-h-screen flex items-center justify-center"
      initial={{ opacity: 0 }}
      whileInView={{ opacity: 1 }}
      viewport={{ once: true }}
      transition={{ duration: 0.5 }}
    >
      <div className="text-center space-y-8">
        {artistStreak.artist_image_url && (
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5 }}
            className="flex justify-center"
          >
            <div className="relative w-48 h-48 rounded-full overflow-hidden ring-4 ring-indigo-500/50">
              <Image
                src={artistStreak.artist_image_url}
                alt={artistStreak.artistName}
                fill
                className="object-cover hover:scale-110 transition-transform duration-500"
                sizes="(max-width: 768px) 192px, 192px"
                priority
                onError={(e) => {
                  console.error(
                    "Image failed to load:",
                    artistStreak.artist_image_url
                  );
                  e.currentTarget.src = "/fallback-artist-image.jpg";
                }}
              />
            </div>
          </motion.div>
        )}

        <div className="space-y-6">
          <div className="text-3xl font-bold">
            You listened to{" "}
            <motion.span
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.3 }}
              className="text-pink-400 font-bold block mt-2"
            >
              {artistStreak.artistName}
            </motion.span>{" "}
            for{" "}
            <motion.span
              initial={{ opacity: 0 }}
              whileInView={{ opacity: 1 }}
              viewport={{ once: true }}
              transition={{ delay: 0.5 }}
              className="text-yellow-400 font-bold"
            >
              <CountUp end={artistStreak.streak} duration={2} /> days
            </motion.span>{" "}
            straight!
          </div>

          <motion.div
            className="text-gray-400"
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            transition={{ delay: 0.7 }}
          >
            From {formattedStartDate} to {formattedEndDate}
          </motion.div>

          {/* <motion.div
            className="text-sm text-gray-500"
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            transition={{ delay: 0.9 }}
          >
            That's {Math.floor(artistStreak.totalMinutes / 60)} hours of pure
            dedication!
          </motion.div> */}
        </div>
      </div>
    </motion.div>
  );
}
