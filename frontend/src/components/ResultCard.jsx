import React, { useState } from 'react';

function ResultCard({ result }) {
    const [copied, setCopied] = useState(false);

    // The short URL comes back from the API like "http://localhost:8000/knaXiu"
    const urlToCopy = result.short_url;

    const handleCopy = async () => {
        try {
            await navigator.clipboard.writeText(urlToCopy);
            setCopied(true);
            setTimeout(() => setCopied(false), 2000);
        } catch (err) {
            console.error('Failed to copy', err);
        }
    };

    return (
        <div className="result-card animate-fade-in">
            <div className="success-header">
                <svg className="check-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
                <span>URL shortened successfully!</span>
            </div>

            <div className="url-display group">
                <div className="url-link-wrapper">
                    <a
                        href={urlToCopy}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="short-link"
                    >
                        {urlToCopy}
                    </a>
                </div>

                <button
                    onClick={handleCopy}
                    className={`copy-btn ${copied ? 'copied' : ''}`}
                    title="Copy to clipboard"
                >
                    {copied ? 'Copied!' : 'Copy'}
                </button>
            </div>

            <div className="original-url-display">
                <span className="label">Dest:</span>
                <span className="value" title={result.original_url}>
                    {result.original_url}
                </span>
            </div>

            <style>{`
        .result-card {
          margin-top: 2rem;
          padding-top: 2rem;
          border-top: 1px solid var(--border-color);
        }
        .success-header {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          color: var(--success);
          font-weight: 500;
          margin-bottom: 1rem;
        }
        .check-icon {
          width: 20px;
          height: 20px;
        }
        .url-display {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          background: rgba(15, 23, 42, 0.8);
          padding: 0.5rem 0.5rem 0.5rem 1rem;
          border-radius: 8px;
          border: 1px solid rgba(16, 185, 129, 0.2);
          margin-bottom: 1rem;
        }
        .url-link-wrapper {
          flex: 1;
          overflow: hidden;
        }
        .short-link {
          color: var(--primary);
          text-decoration: none;
          font-weight: 600;
          font-size: 1.125rem;
          word-break: break-all;
          transition: color 0.2s;
        }
        .short-link:hover {
          color: #818cf8;
          text-decoration: underline;
        }
        .copy-btn {
          margin: 0;
          height: auto;
          padding: 0.5rem 1rem;
          font-size: 0.875rem;
          background: rgba(99, 102, 241, 0.1);
          color: var(--primary);
        }
        .copy-btn:hover {
          background: rgba(99, 102, 241, 0.2);
          transform: none;
        }
        .copy-btn.copied {
          background: var(--success);
          color: white;
        }
        .original-url-display {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          font-size: 0.875rem;
        }
        .label {
          color: var(--text-muted);
        }
        .value {
          color: #cbd5e1;
          white-space: nowrap;
          overflow: hidden;
          text-overflow: ellipsis;
        }
      `}</style>
        </div>
    );
}

export default ResultCard;
