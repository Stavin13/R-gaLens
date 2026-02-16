import React, { useState } from 'react';
import { Search, BookOpen, Mic2 } from 'lucide-react';

export default function Dashboard() {
    const [query, setQuery] = useState('');
    const [results, setResults] = useState([]);
    const [loading, setLoading] = useState(false);

    const handleSearch = async (e) => {
        e.preventDefault();
        if (!query) return;

        setLoading(true);
        try {
            const response = await fetch(`/api/v1/analysis/search?query=${encodeURIComponent(query)}`);
            const data = await response.json();
            // Mock data structure adjustment if needed
            setResults(data.results?.ids?.[0] ? data.results.ids[0].map((id, i) => ({
                id,
                text: data.results.documents[0][i],
                metadata: data.results.metadatas[0][i]
            })) : []);
        } catch (error) {
            console.error("Search failed", error);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="dashboard">
            <div className="search-section">
                <form onSubmit={handleSearch} className="search-form">
                    <input
                        type="text"
                        value={query}
                        onChange={(e) => setQuery(e.target.value)}
                        placeholder="Search for terms (e.g., 'Mārga', 'Tāla evolution')..."
                    />
                    <button type="submit" disabled={loading}>
                        <Search size={18} /> Search
                    </button>
                </form>
            </div>

            <div className="results-section">
                <h3>Results</h3>
                {loading ? <p>Searching...</p> : (
                    <div className="results-grid">
                        {results.map((res) => (
                            <div key={res.id} className="result-card">
                                <h4><BookOpen size={16} /> {res.metadata.title || "Untitled Document"}</h4>
                                <p className="metadata">{res.metadata.author || "Unknown Author"} ({res.metadata.year || "n.d."})</p>
                                <p className="snippet">...{res.text.substring(0, 200)}...</p>
                                <div className="tags">
                                    <span className="tag">Score: {(1).toFixed(2)}</span>
                                </div>
                            </div>
                        ))}
                        {results.length === 0 && !loading && <p>No results found or search not initiated.</p>}
                    </div>
                )}
            </div>
        </div>
    );
}
