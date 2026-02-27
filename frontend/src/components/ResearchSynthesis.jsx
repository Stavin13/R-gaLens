import React, { useState } from 'react';
import { Search, History, Loader2, BookOpen, AlertCircle } from 'lucide-react';

export default function ResearchSynthesis() {
    const [term, setTerm] = useState('Marga');
    const [report, setReport] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const primaryTerms = ["Marga", "Raagas", "Taala", "Prabandha", "Desi", "Vaadya"];

    const handleSynthesize = async (e) => {
        if (e) e.preventDefault();
        setLoading(true);
        setError(null);
        try {
            const response = await fetch(`http://localhost:8000/api/v1/analysis/synthesis?term=${encodeURIComponent(term)}`);
            if (!response.ok) {
                const errData = await response.json();
                throw new Error(errData.detail || "Synthesis failed");
            }
            const data = await response.json();
            setReport(data);
        } catch (err) {
            console.error("Synthesis error:", err);
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="synthesis-container">
            <div className="synthesis-controls">
                <h2>Rigorous Academic Synthesis</h2>
                <div className="term-selector">
                    {primaryTerms.map(t => (
                        <button
                            key={t}
                            onClick={() => setTerm(t)}
                            className={term === t ? 'active' : ''}
                        >
                            {t}
                        </button>
                    ))}
                    <div className="custom-input">
                        <input
                            type="text"
                            placeholder="Custom term..."
                            value={term}
                            onChange={(e) => setTerm(e.target.value)}
                        />
                        <button onClick={handleSynthesize} disabled={loading}>
                            {loading ? <Loader2 className="animate-spin" size={18} /> : <History size={18} />}
                            Generate Synthesis
                        </button>
                    </div>
                </div>
            </div>

            {error && (
                <div className="error-banner">
                    <AlertCircle size={20} />
                    <p>{error}</p>
                </div>
            )}

            {loading && (
                <div className="loading-state">
                    <Loader2 className="animate-spin" size={48} />
                    <p>Performing rigorous multi-document analysis using OpenRouter...</p>
                    <p className="subtext">This may take 30-60 seconds as we process all available decade data.</p>
                </div>
            )}

            {report && !loading && (
                <div className="report-display fade-in">
                    <header className="report-header">
                        <h3>Research Report: {report.concept}</h3>
                        <div className="badge">Academic Synthesis</div>
                    </header>

                    <div className="decades-list">
                        {report.decades.map((d, i) => (
                            <section key={i} className="decade-card">
                                <div className="decade-sidebar">
                                    <span className="decade-tag">{d.decade}</span>
                                </div>
                                <div className="decade-content">
                                    <div className="section">
                                        <h4>What was spoken about</h4>
                                        <ul>{d.what_spoken.map((item, idx) => <li key={idx}>{item}</li>)}</ul>
                                    </div>
                                    <div className="section">
                                        <h4>What was discussed</h4>
                                        <ul>{d.what_discussed.map((item, idx) => <li key={idx}>{item}</li>)}</ul>
                                    </div>
                                    <div className="section">
                                        <h4>New discussion</h4>
                                        <p className={d.new_discussion[0]?.includes('No significant') ? 'muted' : 'highlight'}>
                                            {Array.isArray(d.new_discussion) ? d.new_discussion.join(', ') : d.new_discussion}
                                        </p>
                                    </div>
                                </div>
                            </section>
                        ))}
                    </div>
                </div>
            )}

            {!report && !loading && !error && (
                <div className="empty-state">
                    <BookOpen size={64} opacity={0.2} />
                    <p>Select a term and click "Generate Synthesis" to start the analysis.</p>
                </div>
            )}
        </div>
    );
}
