'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';

interface SearchHeaderProps {
  onSearch: (query: string) => Promise<void>;
  isSearching: boolean;
}

export const SearchHeader = ({ onSearch, isSearching }: SearchHeaderProps) => {
  const [query, setQuery] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSearch(query);
  };

  const containerVariants = {
    initial: { opacity: 0, y: -20 },
    animate: {
      opacity: 1,
      y: 0,
      transition: {
        duration: 0.6,
        ease: 'easeOut',
      },
    },
  };

  const inputVariants = {
    focus: {
      boxShadow: '0 0 0 3px rgba(245, 158, 11, 0.3)',
      transition: { duration: 0.2 },
    },
  };

  return (
    <motion.section
      className="w-full max-w-3xl mx-auto px-4 sm:px-6"
      variants={containerVariants}
      initial="initial"
      animate="animate"
    >
      <div className="text-center mb-8 sm:mb-12">
        <motion.h1
          className="text-4xl sm:text-5xl lg:text-6xl font-serif font-bold text-amber-400 mb-4 tracking-tight"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2, duration: 0.6 }}
        >
          Music Academy
        </motion.h1>
        <motion.p
          className="text-lg sm:text-xl text-zinc-400 font-light"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.4, duration: 0.6 }}
        >
          Explore 90 years of historical journals (1930–2023)
        </motion.p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <motion.div
          className="relative group"
          variants={inputVariants}
          whileFocus="focus"
        >
          {/* Glass background effect */}
          <div className="absolute inset-0 rounded-lg bg-gradient-to-r from-zinc-900/40 to-zinc-800/40 backdrop-blur-xl border border-zinc-700/50 pointer-events-none" />

          <div className="relative flex gap-3 items-center p-2">
            <Input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search journals by term (e.g., 'Raagas', 'Marga', 'Taala')"
              className="flex-1 bg-transparent border-0 text-base sm:text-lg lg:text-xl text-white placeholder-zinc-500 focus:outline-none placeholder-opacity-70 px-3"
              disabled={isSearching}
              aria-label="Search journals"
            />
            <Button
              type="submit"
              disabled={isSearching || !query.trim()}
              className="px-6 sm:px-8 py-3 sm:py-4 text-base sm:text-lg font-semibold bg-amber-500 hover:bg-amber-400 text-black rounded-lg disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 hover:scale-105 active:scale-95 flex-shrink-0"
              aria-label="Search button"
            >
              {isSearching ? (
                <span className="flex items-center gap-2">
                  <motion.div
                    animate={{ rotate: 360 }}
                    transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                    className="w-4 h-4 border-2 border-black border-t-transparent rounded-full"
                  />
                  Searching
                </span>
              ) : (
                'Consult'
              )}
            </Button>
          </div>
        </motion.div>

        {/* Accessibility note */}
        <p className="text-sm text-zinc-600 text-center">
          Press Enter or click Consult to search
        </p>
      </form>
    </motion.section>
  );
};
