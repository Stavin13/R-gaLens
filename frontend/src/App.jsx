import React, { useState } from 'react';
import Upload from './components/Upload';
import Dashboard from './components/Dashboard';
import ResearchSynthesis from './components/ResearchSynthesis';
import './App.css';

function App() {
    const [activeTab, setActiveTab] = useState('synthesis');

    return (
        <div className="app-container">
            <header className="app-header">
                <div className="logo-section">
                    <h1>Musicology Research Assistant</h1>
                    <span className="version">v2.0 Beta</span>
                </div>
                <nav>
                    <button
                        className={activeTab === 'upload' ? 'active' : ''}
                        onClick={() => setActiveTab('upload')}
                    >
                        Data Ingestion
                    </button>
                    <button
                        className={activeTab === 'dashboard' ? 'active' : ''}
                        onClick={() => setActiveTab('dashboard')}
                    >
                        Granular Search
                    </button>
                    <button
                        className={activeTab === 'synthesis' ? 'active' : ''}
                        onClick={() => setActiveTab('synthesis')}
                    >
                        Theory Synthesis
                    </button>
                </nav>
            </header>

            <main className="app-content">
                {activeTab === 'upload' && <Upload />}
                {activeTab === 'dashboard' && <Dashboard />}
                {activeTab === 'synthesis' && <ResearchSynthesis />}
            </main>
        </div>
    );
}

export default App;
