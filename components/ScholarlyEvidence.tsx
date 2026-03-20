'use client';

import { motion } from 'framer-motion';
import { Citation } from '@/hooks/useJournalSearch';

interface ScholarlyEvidenceProps {
  citations: Citation[];
}

export const ScholarlyEvidence = ({ citations }: ScholarlyEvidenceProps) => {
  const containerVariants = {
    initial: { opacity: 0 },
    animate: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
        delayChildren: 0.3,
      },
    },
  };

  const cardVariants = {
    initial: { opacity: 0, y: 20 },
    animate: {
      opacity: 1,
      y: 0,
      transition: { duration: 0.4, ease: 'easeOut' },
    },
    hover: {
      backgroundColor: 'rgba(245, 158, 11, 0.08)',
      borderColor: 'rgba(245, 158, 11, 0.5)',
      transition: { duration: 0.2 },
    },
  };

  if (!citations || citations.length === 0) {
    return null;
  }

  return (
    <motion.section
      className="w-full max-w-2xl mx-auto px-4 sm:px-6 pt-8 sm:pt-12"
      variants={containerVariants}
      initial="initial"
      animate="animate"
    >
      <motion.h2
        className="text-2xl sm:text-3xl font-serif font-bold text-amber-400 mb-8 sm:mb-10"
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
      >
        Scholarly Evidence
      </motion.h2>

      <div className="space-y-5 sm:space-y-6">
        {citations.map((citation, index) => (
          <motion.div
            key={index}
            className="group relative rounded-lg border border-zinc-700/50 p-5 sm:p-6 bg-zinc-900/20 backdrop-blur-sm hover:shadow-lg hover:shadow-amber-500/10 transition-all duration-300"
            variants={cardVariants}
            whileHover="hover"
          >
            {/* Hover glow */}
            <div className="absolute inset-0 rounded-lg opacity-0 group-hover:opacity-100 bg-gradient-to-r from-amber-500/10 via-transparent to-transparent blur-xl transition-opacity duration-300 pointer-events-none" />

            <div className="relative space-y-3 sm:space-y-4">
              {/* Publication Year Badge */}
              <div className="flex items-start justify-between gap-3 flex-wrap">
                <h3 className="text-base sm:text-lg font-serif font-bold text-zinc-100 flex-1 min-w-0">
                  {citation.source}
                </h3>
                <motion.div
                  className="flex-shrink-0 inline-flex items-center gap-2 px-3 sm:px-4 py-2 rounded-full bg-amber-500/20 border border-amber-500/50"
                  whileHover={{ scale: 1.05 }}
                >
                  <span className="text-xs sm:text-sm font-semibold text-amber-300">
                    {citation.publicationYear}
                  </span>
                </motion.div>
              </div>

              {/* Additional metadata */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-sm text-zinc-400">
                {citation.author && (
                  <div>
                    <p className="text-xs uppercase tracking-wide text-zinc-500 mb-1">
                      Author
                    </p>
                    <p className="text-zinc-300">{citation.author}</p>
                  </div>
                )}
                {citation.volume && (
                  <div>
                    <p className="text-xs uppercase tracking-wide text-zinc-500 mb-1">
                      Volume
                    </p>
                    <p className="text-zinc-300">{citation.volume}</p>
                  </div>
                )}
              </div>

              {citation.pages && (
                <div className="pt-2 sm:pt-3 border-t border-zinc-700/30">
                  <p className="text-xs uppercase tracking-wide text-zinc-500 mb-1">
                    Pages
                  </p>
                  <p className="text-zinc-300">{citation.pages}</p>
                </div>
              )}
            </div>
          </motion.div>
        ))}
      </div>

      {/* Archive note */}
      <motion.p
        className="text-xs sm:text-sm text-zinc-600 text-center mt-8 sm:mt-10 py-4 sm:py-6 border-t border-zinc-800"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.8 }}
      >
        All sources are from the official Music Academy digital archives spanning 1930–2023
      </motion.p>
    </motion.section>
  );
};
