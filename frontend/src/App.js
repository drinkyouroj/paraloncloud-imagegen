import React, { useState } from 'react';
import './App.css';
import ErrorBoundary from './components/ErrorBoundary';
import ImageGenerator from './components/ImageGenerator';
import ImageEditor from './components/ImageEditor';
import ImageVariation from './components/ImageVariation';
import StyleTransfer from './components/StyleTransfer';

function App() {
  const [activeTab, setActiveTab] = useState('generate');

  const tabs = [
    { id: 'generate', label: 'Generate', icon: '✨' },
    { id: 'edit', label: 'Edit', icon: '✏️' },
    { id: 'variation', label: 'Variations', icon: '🔄' },
    { id: 'style', label: 'Style Transfer', icon: '🎨' },
  ];

  return (
    <ErrorBoundary>
      <div className="App">
        <header className="App-header">
          <h1>🎨 ParalonCloud Image Tool</h1>
          <p>Generate, edit, and transform images using distributed GPU resources</p>
        </header>

        <div className="tabs">
          {tabs.map(tab => (
            <button
              key={tab.id}
              className={`tab ${activeTab === tab.id ? 'active' : ''}`}
              onClick={() => setActiveTab(tab.id)}
            >
              <span className="tab-icon">{tab.icon}</span>
              {tab.label}
            </button>
          ))}
        </div>

        <main className="main-content">
          {activeTab === 'generate' && <ImageGenerator />}
          {activeTab === 'edit' && <ImageEditor />}
          {activeTab === 'variation' && <ImageVariation />}
          {activeTab === 'style' && <StyleTransfer />}
        </main>
      </div>
    </ErrorBoundary>
  );
}

export default App;
