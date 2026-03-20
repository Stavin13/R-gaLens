import { useState, useCallback } from 'react';

export interface Citation {
  source: string;
  publicationYear: number;
  volume?: string;
  pages?: string;
  author?: string;
}

export interface SearchResult {
  answer: string;
  citations: Citation[];
}

export const useJournalSearch = () => {
  const [isSearching, setIsSearching] = useState(false);
  const [result, setResult] = useState<SearchResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSearch = useCallback(async (query: string) => {
    if (!query.trim()) {
      setError('Please enter a search term');
      return;
    }

    setIsSearching(true);
    setError(null);
    setResult(null);

    try {
      const response = await fetch('http://localhost:8000/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'An error occurred during search';
      setError(errorMessage);
      console.error('[v0] Search error:', err);
    } finally {
      setIsSearching(false);
    }
  }, []);

  return {
    isSearching,
    result,
    error,
    handleSearch,
  };
};
