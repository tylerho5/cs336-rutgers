"use client";

import { useState } from 'react';
import { Send, Sparkles, Loader2 } from 'lucide-react';

interface QueryInputProps {
  onSubmit: (query: string) => void;
  isLoading: boolean;
}

export function QueryInput({ onSubmit, isLoading }: QueryInputProps) {
  const [query, setQuery] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      onSubmit(query.trim());
    }
  };

  const exampleQueries = [
    "What is the average loan amount in the database?",
    "What is the most common loan denial reason?",
    "How many mortgages have a loan value greater than the applicant income?"
  ];

  const handleExampleClick = (example: string) => {
    setQuery(example);
  };

  return (
    <div className="w-full space-y-6">
      <div className="text-center space-y-2">
        <h2 className="text-2xl font-bold text-gray-900">Natural Language SQL Query</h2>
        <p className="text-gray-600 max-w-lg mx-auto">
          Ask questions about the loan application database in plain English
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="relative">
          <div className="absolute inset-y-0 left-3 flex items-center pointer-events-none">
            <Sparkles className="h-5 w-5 text-gray-400" />
          </div>
          <textarea
            id="query"
            className="min-h-32 w-full rounded-xl border border-gray-300 bg-white pl-10 pr-16 py-3 text-sm shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 resize-none"
            placeholder="e.g., What is the average loan amount in the database?"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            disabled={isLoading}
          />
          <button
            type="submit"
            className="absolute bottom-3 right-3 rounded-lg bg-emerald-600 p-2 text-white hover:bg-emerald-700 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:ring-offset-2 disabled:opacity-50 transition-colors"
            disabled={isLoading || !query.trim()}
          >
            {isLoading ? (
              <Loader2 className="h-5 w-5 animate-spin" />
            ) : (
              <Send className="h-5 w-5" />
            )}
          </button>
        </div>

        {!isLoading && (
          <div className="space-y-2">
            <p className="text-sm text-gray-600 font-medium">Try these example queries:</p>
            <div className="flex flex-wrap gap-2">
              {exampleQueries.map((example, index) => (
                <button
                  key={index}
                  type="button"
                  onClick={() => handleExampleClick(example)}
                  className="inline-flex items-center rounded-full bg-emerald-50 px-3 py-1 text-xs font-medium text-emerald-700 hover:bg-emerald-100 focus:outline-none focus:ring-2 focus:ring-emerald-500 transition-colors"
                >
                  {example}
                </button>
              ))}
            </div>
          </div>
        )}
        
        {isLoading && (
          <div className="rounded-lg bg-emerald-50 p-4">
            <div className="flex">
              <div className="flex-shrink-0">
                <Loader2 className="h-5 w-5 text-emerald-600 animate-spin" />
              </div>
              <div className="ml-3">
                <h3 className="text-sm font-medium text-emerald-800">Processing your query</h3>
                <div className="mt-2 text-sm text-emerald-700">
                  <p>
                    This can take up to several minutes as the system:
                  </p>
                  <ol className="list-decimal ml-5 mt-1 space-y-1">
                    <li>Converts your question to relational algebra</li>
                    <li>Generates an optimized SQL query</li>
                    <li>Executes the query on the database</li>
                  </ol>
                  <div className="h-1.5 w-full bg-emerald-200 rounded-full mt-3 overflow-hidden">
                    <div className="h-full bg-emerald-600 rounded-full animate-progress"></div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </form>
    </div>
  );
} 