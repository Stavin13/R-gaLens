'use client';

import { motion } from 'framer-motion';
import { SearchResult } from '@/hooks/useJournalSearch';

interface ResultsDisplayProps {
  result: SearchResult;
}

export const ResultsDisplay = ({ result }: ResultsDisplayProps) => {
  const containerVariants = {
    initial: { opacity: 0, y: 20 },
    animate: {
      opacity: 1,
      y: 0,
      transition: {
        duration: 0.5,
        ease: 'easeOut',
      },
    },
  };

  const textVariants = {
    initial: { opacity: 0 },
    animate: { opacity: 1 },
  };

  // Extract first character for drop-cap
  const answer = result.answer || '';
  const firstChar = answer.charAt(0);
  const restOfText = answer.slice(1);

  return (
    <motion.section
      className="w-full max-w-2xl mx-auto px-4 sm:px-6"
      variants={containerVariants}
      initial="initial"
      animate="animate"
    >
      {/* Answer with Drop-cap */}
      <motion.div
        className="prose prose-invert max-w-none mb-10 sm:mb-12"
        variants={textVariants}
        transition={{ delay: 0.2 }}
      >
        <div className="space-y-4 sm:space-y-6">
          {/* Drop-cap styling */}
          <p className="text-lg sm:text-2xl lg:text-3xl leading-relaxed sm:leading-relaxed text-zinc-200 font-light">
            <span
              className="float-left text-6xl sm:text-7xl lg:text-8xl font-serif font-bold text-amber-400 leading-none mr-3 sm:mr-4 -mt-1"
              role="presentation"
            >
              {firstChar}
            </span>
            <span className="font-serif">{restOfText}</span>
          </p>

          {/* Additional paragraphs if answer is long */}
          {answer.length > 200 && (
            <motion.p
              className="text-lg sm:text-2xl lg:text-3xl leading-relaxed text-zinc-200 font-light font-serif"
              variants={textVariants}
              transition={{ delay: 0.4 }}
            >
              This information comes from carefully preserved historical records spanning nearly a century of music academy documentation.
            </motion.p>
          )}
        </div>
      </motion.div>

      {/* Divider */}
      <motion.div
        className="h-px bg-gradient-to-r from-transparent via-zinc-700 to-transparent my-10 sm:my-12"
        initial={{ scaleX: 0 }}
        animate={{ scaleX: 1 }}
        transition={{ delay: 0.5, duration: 0.8 }}
      />
    </motion.section>
  );
};
