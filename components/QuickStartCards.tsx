'use client';

import { motion } from 'framer-motion';
import { Button } from '@/components/ui/button';

interface QuickStartCardsProps {
  onSelect: (term: string) => void;
  isSearching: boolean;
}

const quickTerms = [
  { label: 'Raagas', description: 'Indian melodic frameworks' },
  { label: 'Marga', description: 'Classical musical traditions' },
  { label: 'Taala', description: 'Rhythmic patterns' },
  { label: 'Desi', description: 'Folk and regional music' },
  { label: 'Gharana', description: 'Musical schools and lineages' },
  { label: 'Hindustani', description: 'North Indian classical' },
];

export const QuickStartCards = ({ onSelect, isSearching }: QuickStartCardsProps) => {
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
      scale: 1.05,
      backgroundColor: 'rgba(245, 158, 11, 0.15)',
      transition: { duration: 0.2 },
    },
  };

  return (
    <motion.section
      className="w-full max-w-4xl mx-auto px-4 sm:px-6 py-12 sm:py-16"
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
        Quick Start Terms
      </motion.h2>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-5">
        {quickTerms.map((term, index) => (
          <motion.button
            key={index}
            onClick={() => onSelect(term.label)}
            disabled={isSearching}
            className="group relative h-full"
            variants={cardVariants}
            whileHover="hover"
            whileTap={{ scale: 0.98 }}
          >
            {/* Card background with border */}
            <div className="absolute inset-0 rounded-lg border border-zinc-700/50 bg-zinc-900/30 backdrop-blur-sm group-hover:border-amber-500/50 transition-all duration-200" />

            {/* Hover glow effect */}
            <div className="absolute inset-0 rounded-lg opacity-0 group-hover:opacity-100 bg-gradient-to-br from-amber-500/20 to-transparent blur-xl transition-opacity duration-300 pointer-events-none" />

            <div className="relative p-5 sm:p-6 h-full flex flex-col justify-center items-start disabled:opacity-50 disabled:cursor-not-allowed">
              <h3 className="text-lg sm:text-xl font-serif font-bold text-amber-400 mb-2 text-left">
                {term.label}
              </h3>
              <p className="text-sm sm:text-base text-zinc-400 text-left line-clamp-2">
                {term.description}
              </p>
            </div>
          </motion.button>
        ))}
      </div>

      <motion.p
        className="text-sm sm:text-base text-zinc-500 text-center mt-10 sm:mt-12"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.8 }}
      >
        Or search any term above to explore the archives
      </motion.p>
    </motion.section>
  );
};
