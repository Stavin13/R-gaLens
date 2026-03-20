'use client';

import { motion } from 'framer-motion';

export const SkeletonLoader = () => {
  const shimmerVariants = {
    animate: {
      backgroundPosition: ['200% 0', '-200% 0'],
      transition: {
        duration: 2,
        repeat: Infinity,
        ease: 'linear',
      },
    },
  };

  return (
    <div className="w-full max-w-2xl mx-auto space-y-6">
      {/* Main answer skeleton */}
      <div className="space-y-4">
        <motion.div
          className="h-8 w-full rounded bg-gradient-to-r from-zinc-800 via-zinc-700 to-zinc-800 bg-[length:200%_100%]"
          variants={shimmerVariants}
          animate="animate"
        />
        <motion.div
          className="h-6 w-5/6 rounded bg-gradient-to-r from-zinc-800 via-zinc-700 to-zinc-800 bg-[length:200%_100%]"
          variants={shimmerVariants}
          animate="animate"
          transition={{ delay: 0.1 }}
        />
        <motion.div
          className="h-6 w-4/6 rounded bg-gradient-to-r from-zinc-800 via-zinc-700 to-zinc-800 bg-[length:200%_100%]"
          variants={shimmerVariants}
          animate="animate"
          transition={{ delay: 0.2 }}
        />
      </div>

      {/* Citations skeleton */}
      <div className="space-y-3 pt-4 border-t border-zinc-800">
        <motion.div
          className="h-6 w-32 rounded bg-gradient-to-r from-zinc-800 via-zinc-700 to-zinc-800 bg-[length:200%_100%]"
          variants={shimmerVariants}
          animate="animate"
        />
        {[0, 1, 2].map((i) => (
          <motion.div
            key={i}
            className="h-20 w-full rounded border border-zinc-800 bg-gradient-to-r from-zinc-900 via-zinc-800 to-zinc-900 bg-[length:200%_100%]"
            variants={shimmerVariants}
            animate="animate"
            transition={{ delay: 0.1 * i }}
          />
        ))}
      </div>
    </div>
  );
};
