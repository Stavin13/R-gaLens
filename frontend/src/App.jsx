import React, { useState } from 'react';
import Upload from './components/Upload';
import Dashboard from './components/Dashboard';
import './App.css';

function App() {
    const [activeTab, setActiveTab] = useState('dashboard');

    return (
        <div className="app-container">
            <header className="app-header">
                <h1>Musicology Research Assistant</h1>
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
                        Research Dashboard
                    </button>
                </nav>
            </header>

            <main className="app-content">
                {activeTab === 'upload' ? <Upload /> : <Dashboard />}
            </main>
        </div>
    );
}

export default App;
