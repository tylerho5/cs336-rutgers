"use client";

import { useState } from 'react';
import { QueryInput } from '../components/ui/query-input';
import { ResultsDisplay } from '../components/ui/results-display';
import { submitQuery } from '../services/api';

export default function Home() {
  const [isLoading, setIsLoading] = useState(false);
  const [results, setResults] = useState<{
    originalQuery: string;
    sqlQuery: string;
    relationalAlgebra: string;
    llmOutput: string;
    results: string;
    error: string | null;
  } | null>(null);

  const handleQuerySubmit = async (query: string) => {
    setIsLoading(true);
    try {
      const response = await submitQuery(query);
      setResults({
        originalQuery: response.original_query,
        sqlQuery: response.sql_query,
        relationalAlgebra: response.relational_algebra,
        llmOutput: response.llm_output,
        results: response.results,
        error: response.error,
      });
    } catch (error) {
      console.error('Error:', error);
      setResults({
        originalQuery: query,
        sqlQuery: '',
        relationalAlgebra: '',
        llmOutput: '',
        results: '',
        error: 'Failed to process query. Please try again.',
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleReset = () => {
    setResults(null);
  };

  return (
    <div className="flex min-h-screen flex-col bg-gray-50">
      <header className="border-b border-gray-200 bg-white py-4">
        <div className="container mx-auto px-4 flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Natural Language Database Interface</h1>
            <p className="text-gray-600">Ask questions about the database in plain English</p>
          </div>
          {isLoading && (
            <div className="flex items-center rounded-full bg-blue-50 px-3 py-1 text-sm text-blue-600">
              <svg className="mr-2 h-4 w-4 animate-spin text-blue-600" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
              </svg>
              Processing...
            </div>
          )}
        </div>
      </header>

      <main className="container mx-auto flex-1 px-4 py-8">
        <div className="mx-auto max-w-4xl">
          {!results ? (
            <div className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
              <QueryInput onSubmit={handleQuerySubmit} isLoading={isLoading} />
            </div>
          ) : (
            <ResultsDisplay
              originalQuery={results.originalQuery}
              sqlQuery={results.sqlQuery}
              relationalAlgebra={results.relationalAlgebra}
              llmOutput={results.llmOutput}
              results={results.results}
              error={results.error}
              onReset={handleReset}
            />
          )}
        </div>
      </main>

      <footer className="border-t border-gray-200 bg-white py-4">
        <div className="container mx-auto px-4 text-center text-sm text-gray-600">
          <p>CS336 Extra Credit Project - Natural Language Database Interface</p>
        </div>
      </footer>
    </div>
  );
}
