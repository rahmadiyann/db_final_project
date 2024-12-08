"use client";

import { motion } from "framer-motion";
import { useState, useEffect } from "react";
import CountUp from "react-countup";
import { useRouter } from "next/navigation";

const musicFacts = [
  "The longest recorded pop song is 'In The Garden' by PC III, lasting 24 hours! 🎵",
  "The shortest song ever recorded is 'You Suffer' by Napalm Death - just 1.316 seconds long! ⚡",
  "The most expensive music video ever made was 'Scream' by Michael and Janet Jackson ($7 million)! 🎥",
  "The first song ever played on MTV was 'Video Killed The Radio Star' by The Buggles! 📺",
  "The Beatles' 'Yesterday' is the most covered song in history! 🎸",
];

interface Question {
  question: string;
  options: string[];
  answer: number;
  explanation: string;
}

const musicQuiz: Question[] = [
  {
    question:
      "What was the first music video to hit 1 billion views on YouTube?",
    options: [
      "Baby - Justin Bieber",
      "Gangnam Style - PSY",
      "Bad Romance - Lady Gaga",
      "Never Gonna Give You Up - Rick Astley",
    ],
    answer: 1,
    explanation:
      "PSY's 'Gangnam Style' was the first video to break the billion-view barrier in 2012! 🎉",
  },
  {
    question: "Which of these albums is the best-selling of all time?",
    options: [
      "Back in Black - AC/DC",
      "Thriller - Michael Jackson",
      "The Dark Side of the Moon - Pink Floyd",
      "Abbey Road - The Beatles",
    ],
    answer: 1,
    explanation:
      "Michael Jackson's 'Thriller' has sold over 70 million copies worldwide! 🎶",
  },
  {
    question: "Who is known as the 'Queen of Pop'?",
    options: ["Madonna", "Britney Spears", "Lady Gaga", "Beyoncé"],
    answer: 0,
    explanation: "Madonna is widely recognized as the 'Queen of Pop'. 👑",
  },
  {
    question: "Which band was originally called 'The Quarrymen'?",
    options: ["The Rolling Stones", "The Beatles", "The Who", "The Kinks"],
    answer: 1,
    explanation: "The Beatles were originally known as 'The Quarrymen'. 🎸",
  },
  {
    question: "What is the highest-selling single of all time?",
    options: [
      "White Christmas - Bing Crosby",
      "Candle in the Wind - Elton John",
      "I Will Always Love You - Whitney Houston",
      "Shape of You - Ed Sheeran",
    ],
    answer: 0,
    explanation:
      "'White Christmas' by Bing Crosby is the best-selling single of all time. ❄️",
  },
  {
    question: "Which artist has won the most Grammy Awards?",
    options: ["Beyoncé", "Stevie Wonder", "Quincy Jones", "Georg Solti"],
    answer: 3,
    explanation:
      "Georg Solti holds the record for the most Grammy Awards won. 🏆",
  },
  {
    question:
      "Which song spent the longest time at number one on the Billboard Hot 100?",
    options: [
      "Old Town Road - Lil Nas X",
      "Despacito - Luis Fonsi",
      "One Sweet Day - Mariah Carey and Boyz II Men",
      "I Will Always Love You - Whitney Houston",
    ],
    answer: 0,
    explanation:
      "'Old Town Road' by Lil Nas X spent 19 weeks at number one. 🐎",
  },
  {
    question:
      "Who was the first woman inducted into the Rock and Roll Hall of Fame?",
    options: [
      "Aretha Franklin",
      "Janis Joplin",
      "Tina Turner",
      "Joni Mitchell",
    ],
    answer: 0,
    explanation:
      "Aretha Franklin was the first woman inducted into the Rock and Roll Hall of Fame. 🎤",
  },
  {
    question: "Which band is known for the album 'The Wall'?",
    options: ["Led Zeppelin", "Pink Floyd", "The Doors", "Queen"],
    answer: 1,
    explanation: "'The Wall' is a famous album by Pink Floyd. 🧱",
  },
  {
    question: "What is the best-selling digital single of all time?",
    options: [
      "Rolling in the Deep - Adele",
      "Uptown Funk - Mark Ronson ft. Bruno Mars",
      "Shape of You - Ed Sheeran",
      "Despacito - Luis Fonsi",
    ],
    answer: 2,
    explanation:
      "'Shape of You' by Ed Sheeran is the best-selling digital single of all time. 🎶",
  },
  {
    question: "Which artist is known as the 'King of Pop'?",
    options: ["Elvis Presley", "Michael Jackson", "Prince", "Freddie Mercury"],
    answer: 1,
    explanation: "Michael Jackson is famously known as the 'King of Pop'. 👑",
  },
  {
    question: "Which song is the most streamed on Spotify?",
    options: [
      "Blinding Lights - The Weeknd",
      "Shape of You - Ed Sheeran",
      "Dance Monkey - Tones and I",
      "Rockstar - Post Malone",
    ],
    answer: 1,
    explanation:
      "'Shape of You' by Ed Sheeran is the most streamed song on Spotify. 🎧",
  },
  {
    question: "Which artist is known for the hit song 'Purple Rain'?",
    options: ["Prince", "David Bowie", "Freddie Mercury", "Elton John"],
    answer: 0,
    explanation: "'Purple Rain' is a famous song by Prince. ☔️",
  },
  {
    question: "Which band released the album 'Rumours'?",
    options: ["Fleetwood Mac", "The Eagles", "The Beach Boys", "The Doors"],
    answer: 0,
    explanation: "'Rumours' is a classic album by Fleetwood Mac. 🎶",
  },
  {
    question: "Who is known as the 'Queen of Soul'?",
    options: [
      "Aretha Franklin",
      "Whitney Houston",
      "Diana Ross",
      "Tina Turner",
    ],
    answer: 0,
    explanation: "Aretha Franklin is famously known as the 'Queen of Soul'. 👑",
  },
  {
    question: "Which artist released the song 'Thriller'?",
    options: ["Michael Jackson", "Prince", "Madonna", "Whitney Houston"],
    answer: 0,
    explanation: "'Thriller' is a famous song by Michael Jackson. 🎃",
  },
  {
    question: "Which band is known for the song 'Bohemian Rhapsody'?",
    options: ["Queen", "The Beatles", "The Rolling Stones", "Led Zeppelin"],
    answer: 0,
    explanation: "'Bohemian Rhapsody' is a famous song by Queen. 🎤",
  },
];

export default function EmptyState() {
  const router = useRouter();
  const [currentFact, setCurrentFact] = useState(0);
  const [quizStarted, setQuizStarted] = useState(false);
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [score, setScore] = useState(0);
  const [showAnswer, setShowAnswer] = useState(false);
  const [selectedAnswer, setSelectedAnswer] = useState<number | null>(null);

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentFact((prev) => (prev + 1) % musicFacts.length);
    }, 5000);
    return () => clearInterval(timer);
  }, []);

  useEffect(() => {
    // Check for data every 30 seconds
    const checkDataInterval = setInterval(async () => {
      try {
        const response = await fetch("/api/check-data");
        const { hasData } = await response.json();

        if (hasData) {
          // Refresh the page when data is available
          router.refresh();
        }
      } catch (error) {
        console.error("Error checking data status:", error);
      }
    }, 30000);

    return () => clearInterval(checkDataInterval);
  }, [router]);

  const handleAnswer = (index: number) => {
    setSelectedAnswer(index);
    setShowAnswer(true);
    if (index === musicQuiz[currentQuestion].answer) {
      setScore(score + 1);
    }
  };

  const nextQuestion = () => {
    if (currentQuestion < musicQuiz.length - 1) {
      setCurrentQuestion(currentQuestion + 1);
      setShowAnswer(false);
      setSelectedAnswer(null);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-black text-white">
      <div className="text-center space-y-8 max-w-2xl px-4">
        <motion.h1
          className="text-4xl font-bold"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          Welcome to Your Music Journey! 🎵
        </motion.h1>

        {!quizStarted ? (
          <>
            <motion.div
              className="text-gray-400 space-y-4"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.3 }}
            >
              <p>
                While we wait for your first listening data, did you know...
              </p>
              <motion.div
                key={currentFact}
                initial={{ opacity: 0, x: 50 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -50 }}
                className="text-xl font-medium text-purple-400"
              >
                {musicFacts[currentFact]}
              </motion.div>
            </motion.div>

            <motion.button
              onClick={() => setQuizStarted(true)}
              className="bg-purple-600 hover:bg-purple-700 text-white px-8 py-3 rounded-full font-bold transition-all transform hover:scale-105"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              Take the Music Quiz! 🎯
            </motion.button>
          </>
        ) : (
          <motion.div
            className="space-y-6"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
          >
            <div className="text-2xl font-bold text-purple-400">
              Score: <CountUp end={score} duration={1} /> / {musicQuiz.length}
            </div>

            <motion.div
              key={currentQuestion}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-white/10 p-6 rounded-lg"
            >
              <h2 className="text-xl mb-4">
                {musicQuiz[currentQuestion].question}
              </h2>
              <div className="space-y-3">
                {musicQuiz[currentQuestion].options.map((option, index) => (
                  <motion.button
                    key={index}
                    onClick={() => !showAnswer && handleAnswer(index)}
                    className={`w-full p-3 rounded-lg transition-all ${
                      showAnswer
                        ? index === musicQuiz[currentQuestion].answer
                          ? "bg-green-500"
                          : selectedAnswer === index
                          ? "bg-red-500"
                          : "bg-white/10"
                        : "bg-white/10 hover:bg-white/20"
                    }`}
                    whileHover={!showAnswer ? { scale: 1.02 } : {}}
                    whileTap={!showAnswer ? { scale: 0.98 } : {}}
                    disabled={showAnswer}
                  >
                    {option}
                  </motion.button>
                ))}
              </div>
              {showAnswer && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="mt-4 text-gray-300"
                >
                  {musicQuiz[currentQuestion].explanation}
                  {currentQuestion < musicQuiz.length - 1 && (
                    <motion.button
                      onClick={nextQuestion}
                      className="mt-4 bg-purple-600 hover:bg-purple-700 text-white px-6 py-2 rounded-full"
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                    >
                      Next Question →
                    </motion.button>
                  )}
                </motion.div>
              )}
            </motion.div>
          </motion.div>
        )}

        <motion.div
          className="text-sm text-gray-500"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.6 }}
        >
          Start playing some music and check back soon!
        </motion.div>
      </div>
    </div>
  );
}
