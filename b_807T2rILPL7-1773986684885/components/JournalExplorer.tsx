'use client';

import { useJournalSearch } from '@/hooks/useJournalSearch';
import { SearchHeader } from './SearchHeader';
import { QuickStartCards } from './QuickStartCards';
import { ResultsDisplay } from './ResultsDisplay';
import { ScholarlyEvidence } from './ScholarlyEvidence';
import { SkeletonLoader } from './SkeletonLoader';
import { motion, AnimatePresence } from 'framer-motion';

export const JournalExplorer = () => {
  const { isSearching, result, error, handleSearch } = useJournalSearch();

  const pageVariants = {
    initial: { opacity: 0 },
    animate: {
      opacity: 1,
      transition: {
        duration: 0.4,
        ease: 'easeOut',
      },
    },
  };

  const errorVariants = {
    initial: { opacity: 0, y: -10 },
    animate: { opacity: 1, y: 0 },
    exit: { opacity: 0, y: -10 },
  };

  return (
    <motion.main
      className="min-h-screen bg-black relative overflow-hidden"
      variants={pageVariants}
      initial="initial"
      animate="animate"
    >
      {/* Ambient background elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-amber-900/20 rounded-full blur-3xl -translate-y-1/2" />
        <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-amber-900/10 rounded-full blur-3xl translate-y-1/2" />
      </div>

      {/* Content */}
      <div className="relative z-10 w-full">
        <div className="pt-8 sm:pt-12 md:pt-16 pb-12 sm:pb-16">
          <SearchHeader onSearch={handleSearch} isSearching={isSearching} />

          {/* Error message */}
          <AnimatePresence>
            {error && (
              <motion.div
                className="max-w-2xl mx-auto px-4 sm:px-6 mt-6 sm:mt-8 p-4 sm:p-6 rounded-lg bg-red-900/20 border border-red-800/50"
                variants={errorVariants}
                initial="initial"
                animate="animate"
                exit="exit"
              >
                <p className="text-red-300 text-sm sm:text-base">{error}</p>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Show quick start only when there's no result */}
          <AnimatePresence mode="wait">
            {!result && !isSearching && !error && (
              <QuickStartCards onSelect={handleSearch} isSearching={isSearching} />
            )}
          </AnimatePresence>

          {/* Loading state */}
          <AnimatePresence>
            {isSearching && (
              <motion.div
                className="max-w-2xl mx-auto px-4 sm:px-6 mt-12 sm:mt-16"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
              >
                <SkeletonLoader />
              </motion.div>
            )}
          </AnimatePresence>

          {/* Results section */}
          <AnimatePresence>
            {result && !isSearching && (
              <motion.div
                className="mt-12 sm:mt-16 md:mt-20 space-y-8 sm:space-y-12"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.5 }}
              >
                <ResultsDisplay result={result} />
                {result.citations && result.citations.length > 0 && (
                  <ScholarlyEvidence citations={result.citations} />
                )}
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Footer */}
        <motion.footer
          className="border-t border-zinc-800 py-8 sm:py-12 mt-12 sm:mt-16 relative z-10"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1 }}
        >
          <div className="max-w-4xl mx-auto px-4 sm:px-6 text-center">
            <p className="text-sm sm:text-base text-zinc-500">
              Music Academy Journal Explorer • Powered by RAG • 90 Years of Historical Archives (1930–2023)
            </p>
          </div>
        </motion.footer>
      </div>
    </motion.main>
  );
};
