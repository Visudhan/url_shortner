import React, { useState } from 'react';
import axios from 'axios';
import './index.css';

// Components
import ShortenerForm from './components/ShortenerForm';
import ResultCard from './components/ResultCard';

function App() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleShorten = async (originalUrl, customAlias) => {
    setLoading(true);
    setError('');
    setResult(null);

    try {
      // Due to vite.config.js proxy, /api/urls/ goes to Django!
      const payload = { original_url: originalUrl };
      if (customAlias) {
        payload.custom_alias = customAlias;
      }

      const response = await axios.post('/api/urls/', payload);
      setResult(response.data);
    } catch (err) {
      if (err.response && err.response.data) {
        // DRF error formatting
        const errorData = err.response.data;
        const messages = Object.values(errorData).flat().join(' ');
        setError(messages || 'Failed to shorten URL.');
      } else {
        setError('Network error. Is the backend running?');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-container">
      <header className="hero">
        <h1 className="animate-fade-in">URL Shortener</h1>
        <p className="subtitle animate-fade-in" style={{ animationDelay: '0.1s' }}>
          Fast, clean, and reliable link management.
        </p>
      </header>

      <main className="main-content">
        <div className="glass-panel animate-fade-in" style={{ animationDelay: '0.2s', padding: '2rem' }}>
          <ShortenerForm onSubmit={handleShorten} loading={loading} />

          {error && (
            <div className="error-message">
              {error}
            </div>
          )}

          {result && !loading && (
            <ResultCard result={result} />
          )}
        </div>
      </main>

      <style>{`
        .app-container {
          width: 100%;
          max-width: 600px;
          margin: 0 auto;
        }
        .hero {
          text-align: center;
          margin-bottom: 3rem;
        }
        h1 {
          font-size: 3rem;
          font-weight: 700;
          letter-spacing: -0.05em;
          background: linear-gradient(135deg, #fff 0%, #cbd5e1 100%);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          margin-bottom: 0.5rem;
        }
        .subtitle {
          color: var(--text-muted);
          font-size: 1.125rem;
        }
        .error-message {
          margin-top: 1.5rem;
          padding: 1rem;
          background: rgba(239, 68, 68, 0.1);
          border: 1px solid rgba(239, 68, 68, 0.2);
          border-radius: 8px;
          color: #fca5a5;
          text-align: center;
        }
      `}</style>
    </div>
  );
}

export default App;
