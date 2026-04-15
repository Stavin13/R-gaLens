'use client';

import { motion } from 'framer-motion';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
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

  const answer = result.answer || '';

  return (
    <motion.section
      className="w-full max-w-3xl mx-auto px-4 sm:px-6"
      variants={containerVariants}
      initial="initial"
      animate="animate"
    >
      <div className="prose prose-invert max-w-none mb-10 sm:mb-12">
        <ReactMarkdown
          remarkPlugins={[remarkGfm]}
          components={{
            // Style the Executive Summary or first paragraph differently
            p: ({ children }) => (
              <p className="text-lg sm:text-xl leading-relaxed text-zinc-300 font-serif mb-6 opacity-90">
                {children}
              </p>
            ),
            h3: ({ children }) => (
              <h3 className="text-xl sm:text-2xl font-serif font-bold text-amber-400 mt-10 mb-4 border-b border-zinc-800 pb-2">
                {children}
              </h3>
            ),
            h4: ({ children }) => (
                <h4 className="text-lg font-serif font-semibold text-amber-200/80 mt-6 mb-2">
                  {children}
                </h4>
            ),
            // Style tables for a clean research look
            table: ({ children }) => (
              <div className="my-8 overflow-x-auto rounded-lg border border-zinc-700/50 bg-zinc-900/40">
                <table className="w-full text-sm text-left text-zinc-300">
                  {children}
                </table>
              </div>
            ),
            thead: ({ children }) => (
              <thead className="bg-zinc-800/50 text-amber-400 font-serif lowercase italic">
                {children}
              </thead>
            ),
            th: ({ children }) => (
              <th className="px-4 py-3 font-semibold border-b border-zinc-700">
                {children}
              </th>
            ),
            td: ({ children }) => (
              <th className="px-4 py-3 border-b border-zinc-800/50 font-normal">
                {children}
              </th>
            ),
            // Style citations [1]
            strong: ({ children }) => (
              <strong className="text-amber-300 font-semibold">{children}</strong>
            ),
            blockquote: ({ children }) => (
              <blockquote className="border-l-4 border-amber-500/50 pl-6 my-8 italic text-zinc-400 bg-zinc-900/20 py-4 rounded-r-lg">
                {children}
              </blockquote>
            )
          }}
        >
          {answer}
        </ReactMarkdown>
      </div>

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
