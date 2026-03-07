import React, { useState } from 'react';

function ShortenerForm({ onSubmit, loading }) {
    const [url, setUrl] = useState('');
    const [alias, setAlias] = useState('');

    const handleSubmit = (e) => {
        e.preventDefault();
        if (url.trim()) {
            onSubmit(url.trim(), alias.trim());
        }
    };

    return (
        <form className="shortener-form" onSubmit={handleSubmit}>
            <div className="input-group">
                <label htmlFor="url">Original URL</label>
                <input
                    id="url"
                    type="url"
                    placeholder="https://example.com/very-long-link"
                    value={url}
                    onChange={(e) => setUrl(e.target.value)}
                    required
                    disabled={loading}
                />
            </div>

            <div className="input-group">
                <label htmlFor="alias">Custom Alias (Optional)</label>
                <div className="alias-input-wrapper">
                    <span className="domain-prefix">short.er/</span>
                    <input
                        id="alias"
                        type="text"
                        placeholder="my-link"
                        value={alias}
                        onChange={(e) => setAlias(e.target.value)}
                        pattern="[A-Za-z0-9-]+"
                        title="Letters, numbers, and hyphens only"
                        disabled={loading}
                    />
                </div>
            </div>

            <button type="submit" disabled={loading || !url.trim()} className="submit-btn">
                {loading ? (
                    <span className="loader"></span>
                ) : (
                    'Shorten URL'
                )}
            </button>

            <style>{`
        .shortener-form {
          display: flex;
          flex-direction: column;
          gap: 1.5rem;
        }
        .input-group {
          display: flex;
          flex-direction: column;
          gap: 0.5rem;
        }
        label {
          font-size: 0.875rem;
          font-weight: 500;
          color: var(--text-muted);
        }
        .alias-input-wrapper {
          display: flex;
          align-items: center;
          background: rgba(15, 23, 42, 0.6);
          border: 1px solid var(--border-color);
          border-radius: 8px;
          overflow: hidden;
          transition: all 0.2s ease;
        }
        .alias-input-wrapper:focus-within {
          border-color: var(--primary);
          box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.2);
        }
        .domain-prefix {
          padding: 0 0.5rem 0 1rem;
          color: var(--text-muted);
          font-size: 0.875rem;
          user-select: none;
        }
        .alias-input-wrapper input {
          border: none;
          background: transparent;
          padding-left: 0;
        }
        .alias-input-wrapper input:focus {
          box-shadow: none;
        }
        .submit-btn {
          margin-top: 0.5rem;
          height: 3rem;
        }
        .loader {
          width: 20px;
          height: 20px;
          border: 2px solid rgba(255,255,255,0.3);
          border-radius: 50%;
          border-top-color: #fff;
          animation: spin 0.8s linear infinite;
        }
        @keyframes spin {
          to { transform: rotate(360deg); }
        }
      `}</style>
        </form>
    );
}

export default ShortenerForm;
