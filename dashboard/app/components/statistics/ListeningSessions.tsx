"use client";

import { motion } from "framer-motion";
import CountUp from "react-countup";
import { SessionType } from "../../types/stats";

interface ListeningSessionsProps {
  sessionTypes: SessionType[];
}

export default function ListeningSessions({
  sessionTypes,
}: ListeningSessionsProps) {
  // Find dominant session type
  const dominantSession = [...sessionTypes].sort(
    (a, b) => b.percentage - a.percentage
  )[0];

  const getSessionEmoji = (type: string) => {
    switch (type.toLowerCase()) {
      case "focused":
        return "🎯";
      case "background":
        return "🎶";
      case "party":
        return "🎉";
      case "chill":
        return "😌";
      case "workout":
        return "💪";
      case "commute":
        return "🚗";
      default:
        return "🎵";
    }
  };

  const getSessionDescription = (type: string) => {
    switch (type.toLowerCase()) {
      case "focused":
        return "Deep work mode activated! Your soundtrack for maximum productivity";
      case "background":
        return "Setting the mood while you do your thing";
      case "party":
        return "Turn up the volume, it's time to celebrate! ";
      case "chill":
        return "Keeping it cool and relaxed, vibing with the flow";
      case "workout":
        return "Getting those gains with the perfect beat";
      case "commute":
        return "Making traffic jams a little more bearable";
      default:
        return "Your musical moments";
    }
  };

  const getListenerType = () => {
    const type = dominantSession.sessionType.toLowerCase();
    switch (type) {
      case "focused":
        return "The Productivity Maestro ";
      case "background":
        return "The Ambient Enthusiast ";
      case "party":
        return "The Life of the Party ";
      case "chill":
        return "The Zen Master ";
      case "workout":
        return "The Gym Hero ";
      case "commute":
        return "The Road Warrior ";
      default:
        return "The Versatile Listener ";
    }
  };

  const getListenerDescription = () => {
    const type = dominantSession.sessionType.toLowerCase();
    switch (type) {
      case "focused":
        return "You're all about that productivity playlist! Music is your secret weapon for getting things done. ";
      case "background":
        return "Music is your constant companion, providing the perfect backdrop to your daily adventures. ";
      case "party":
        return "Always ready to hit play on those party bangers! You know how to keep the energy high. ";
      case "chill":
        return "Keeping it cool and collected with your laid-back vibes. Stress? Never heard of it! ";
      case "workout":
        return "Your playlist is your personal trainer - pushing you through one more rep! ";
      case "commute":
        return "Turning every journey into a mini concert. Traffic jams? More like jam sessions! ";
      default:
        return "You've got a playlist for every moment - keeping life interesting one song at a time! ";
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
          <h2 className="text-3xl font-bold">How You Vibe </h2>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 1.5, delay: 0.5 }}
          >
            <p className="text-gray-400 max-w-2xl mx-auto">
              From focused work sessions to full-on party mode, let's see how
              you use music to enhance different moments of your life!
            </p>
          </motion.div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 1.5, delay: 0.5 }}
        >
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {sessionTypes.map((session, index) => (
              <motion.div
                key={index}
                className="bg-white/5 p-6 rounded-lg relative overflow-hidden group"
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.2 }}
              >
                <div className="flex items-center gap-3 mb-2">
                  <span className="text-2xl">
                    {getSessionEmoji(session.sessionType)}
                  </span>
                  <h3 className="text-xl font-bold">{session.sessionType}</h3>
                </div>
                <p className="text-sm text-gray-400 mb-4">
                  {getSessionDescription(session.sessionType)}
                </p>
                <div className="flex justify-between items-end">
                  <div>
                    <div className="text-3xl font-bold text-indigo-400">
                      <CountUp end={session.percentage} duration={2} />%
                    </div>
                    <div className="text-sm text-gray-500">
                      <CountUp end={session.count} duration={2} /> sessions
                    </div>
                  </div>
                </div>
                <motion.div
                  className="absolute bottom-0 left-0 h-1 bg-indigo-400"
                  initial={{ width: 0 }}
                  whileInView={{ width: `${session.percentage}%` }}
                  transition={{ duration: 1 }}
                />
              </motion.div>
            ))}
          </div>
          <div className="text-center space-y-4">
            <div className="bg-white/5 p-6 rounded-lg mt-4">
              <h3 className="text-xl font-bold mb-2">{getListenerType()}</h3>
              <p className="text-gray-400 text-sm mb-4">
                {getListenerDescription()}
              </p>
              <div className="text-sm text-gray-500">
                Most common: {dominantSession.sessionType} (
                {dominantSession.percentage}% of your sessions)
              </div>
            </div>
          </div>
        </motion.div>
      </div>
    </motion.div>
  );
}
