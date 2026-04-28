'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';

export default function SymbolSearch() {
  const [symbol, setSymbol] = useState('');
  const router = useRouter();

  const handleSearch = (e) => {
    e.preventDefault();
    if (symbol.trim()) {
      router.push(`/analyze/${symbol.toUpperCase()}`);
    }
  };

  return (
    <form onSubmit={handleSearch} className="symbol-search">
      <input
        type="text"
        placeholder="Enter any ticker symbol (e.g., AAPL)"
        value={symbol}
        onChange={(e) => setSymbol(e.target.value)}
        className="search-input"
      />
      <button type="submit" className="search-button">
        Analyze Stock →
      </button>
      
      <style jsx>{`
        .symbol-search {
          display: flex;
          gap: 1rem;
          max-width: 500px;
          margin: 2rem auto 3rem;
        }

        .search-input {
          flex: 1;
          padding: 0.875rem 1.25rem;
          font-size: 1rem;
          border: 2px solid #e0e0e0;
          border-radius: 8px;
          transition: border-color 0.2s;
        }

        .search-input:focus {
          outline: none;
          border-color: #1e3c72;
        }

        .search-button {
          padding: 0.875rem 1.5rem;
          background: #1e3c72;
          color: white;
          border: none;
          border-radius: 8px;
          font-weight: 600;
          cursor: pointer;
          transition: background 0.2s;
          white-space: nowrap;
        }

        .search-button:hover {
          background: #2a5298;
        }

        @media (max-width: 640px) {
          .symbol-search {
            flex-direction: column;
          }
          
          .search-button {
            width: 100%;
          }
        }
      `}</style>
    </form>
  );
}