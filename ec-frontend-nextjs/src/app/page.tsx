"use client";

import { useState, useRef, useEffect } from 'react';
import { submitQuery } from '../services/api';
import { Database, Github, Menu, Send, Sparkles, Download } from 'lucide-react';

interface QueryMessage {
  role: 'user' | 'assistant';
  content: string;
  sql?: string;
  relationalAlgebra?: string;
  llmOutput?: string;
  results?: string;
  error?: string | null;
}

export default function Home() {
  const [isLoading, setIsLoading] = useState(false);
  const [query, setQuery] = useState('');
  const [messages, setMessages] = useState<QueryMessage[]>([]);
  const [showHistory, setShowHistory] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  // Example queries
  const exampleQueries = [
    "What is the average loan amount in the database?",
    "What is the most common loan denial reason?",
    "How many mortgages have a loan value greater than the applicant income?"
  ];

  // Focus input on load
  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  // Scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim() || isLoading) return;

    const userQuery = query.trim();
    setQuery('');
    setIsLoading(true);

    // Add user message
    setMessages(prev => [...prev, { role: 'user', content: userQuery }]);

    try {
      const response = await submitQuery(userQuery);
      
      // Add assistant message
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'Here are the results for your query.',
        sql: response.sql_query,
        relationalAlgebra: response.relational_algebra,
        llmOutput: response.llm_output,
        results: response.results,
        error: response.error
      }]);
    } catch (error) {
      console.error('Error:', error);
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'Failed to process query. Please try again.',
        error: 'Failed to process query. Please try again.'
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleExampleClick = (example: string) => {
    setQuery(example);
    inputRef.current?.focus();
  };

  const userQueries = messages.filter(m => m.role === 'user');

  return (
    <div className="flex flex-col h-screen">
      {/* Header */}
      <header className="border-b p-4">
        <div className="container mx-auto flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button
              className="p-2 rounded-md hover:bg-gray-100 focus:outline-none"
              onClick={() => setShowHistory(!showHistory)}
            >
              <Menu className="h-5 w-5" />
            </button>
            <div className="flex items-center gap-2">
              <Database className="h-5 w-5 text-emerald-600" />
              <h1 className="text-xl font-semibold">Natural Language SQL</h1>
            </div>
          </div>
          {isLoading && (
            <div className="flex items-center rounded-full bg-emerald-50 px-3 py-1.5 text-sm text-emerald-600">
              <svg className="mr-2 h-4 w-4 animate-spin text-emerald-600" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
              </svg>
              Processing...
            </div>
          )}
        </div>
      </header>

      <div className="flex flex-1 overflow-hidden">
        {/* History sidebar */}
        {showHistory && (
          <div className="w-64 border-r p-4 overflow-y-auto">
            <h2 className="font-medium text-gray-900 mb-3">Query History</h2>
            <div className="space-y-2">
              {userQueries.length > 0 ? (
                userQueries.map((q, index) => (
                  <div 
                    key={index}
                    className="p-2 rounded hover:bg-gray-100 cursor-pointer text-sm border border-gray-200"
                    onClick={() => setQuery(q.content)}
                  >
                    {q.content.length > 50 ? q.content.substring(0, 50) + '...' : q.content}
                  </div>
                ))
              ) : (
                <p className="text-sm text-gray-500">No queries yet</p>
              )}
            </div>
          </div>
        )}

        {/* Main content */}
        <div className="flex-1 flex flex-col overflow-hidden">
          {/* Messages area */}
          <div className="flex-1 p-4 overflow-y-auto">
            <div className="space-y-6 max-w-4xl mx-auto">
              {messages.length === 0 ? (
                <div className="rounded-lg border border-gray-200 bg-white p-6">
                  <div className="text-center space-y-4">
                    <p className="text-slate-600">
                      Ask questions about your database in plain English. The system will generate SQL, execute it, and
                      show the results.
                    </p>
                    <div className="p-4 bg-slate-100 rounded-lg text-slate-700 text-sm">
                      <p className="font-medium mb-2">Try questions like:</p>
                      <ul className="space-y-2 text-left">
                        {exampleQueries.map((example, index) => (
                          <li 
                            key={index}
                            className="cursor-pointer hover:text-emerald-600 transition-colors"
                            onClick={() => handleExampleClick(example)}
                          >
                            "{example}"
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </div>
              ) : (
                messages.map((message, index) => (
                  <MessageDisplay 
                    key={index} 
                    message={message} 
                  />
                ))
              )}
              <div ref={messagesEndRef} />
            </div>
          </div>

          {/* Input area */}
          <div className="border-t p-4">
            <form onSubmit={handleSubmit} className="container mx-auto flex space-x-2 max-w-4xl">
              <div className="relative flex-1">
                <textarea
                  ref={inputRef}
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="Ask a question about your database..."
                  className="w-full rounded-md border-gray-300 py-3 pl-10 pr-10 shadow-sm focus:border-emerald-500 focus:ring-emerald-500 text-sm min-h-[44px] max-h-24 resize-none border"
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                      e.preventDefault();
                      handleSubmit(e);
                    }
                  }}
                  disabled={isLoading}
                />
                <Sparkles className="absolute left-3 top-3 h-5 w-5 text-gray-400" />
              </div>
              <button
                type="submit"
                disabled={isLoading || !query.trim()}
                className="rounded-md bg-emerald-600 px-4 py-2 text-white hover:bg-emerald-700 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:ring-offset-2 disabled:opacity-50 flex items-center justify-center"
              >
                {isLoading ? "Processing..." : "Query"}
                {!isLoading && <Send className="ml-2 h-4 w-4" />}
              </button>
            </form>
          </div>
        </div>
      </div>

      <footer className="border-t border-gray-200 bg-white py-3">
        <div className="container mx-auto px-4">
          <div className="flex flex-col items-center justify-between gap-2 text-center md:flex-row md:text-left">
            <p className="text-sm text-gray-600">
              Built with FastAPI, Next.js, and LLMs (Phi-3.5-mini & sqlcoder-7b-2)
            </p>
            <div className="flex items-center space-x-4">
              <a 
                href="https://github.com/tylerho5/cs336-rutgers/tree/main" 
                target="_blank" 
                rel="noopener noreferrer"
                className="flex items-center text-sm text-gray-600 hover:text-emerald-600 transition-colors"
              >
                <Github className="mr-1 h-4 w-4" />
                GitHub
              </a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}

// Message component
function MessageDisplay({ message }: { message: QueryMessage }) {
  const [activeTab, setActiveTab] = useState<'message' | 'sql' | 'results'>('results');
  
  const isUser = message.role === 'user';
  
  const parseResults = () => {
    if (!message.results || message.error) return { headers: [], rows: [] };
    
    try {
      const lines = message.results.split('\n').filter(Boolean);
      if (lines.length < 2) return { headers: [], rows: [] };
      
      const headers = lines[0].split(/\s{2,}/).map(h => h.trim()).filter(Boolean);
      const rows = lines.slice(1).map(line => {
        const values = line.split(/\s{2,}/).map(v => v.trim()).filter(Boolean);
        return values;
      });
      
      return { headers, rows };
    } catch (e) {
      console.error('Error parsing results:', e);
      return { headers: [], rows: [] };
    }
  };
  
  const { headers, rows } = message.results ? parseResults() : { headers: [], rows: [] };
  
  // Get table-like data for display
  const hasResults = headers.length > 0 && rows.length > 0;
  
  if (isUser) {
    return (
      <div className="flex items-start ml-auto max-w-3xl">
        <div className="rounded-lg bg-emerald-600 text-white px-4 py-2 max-w-[85%]">
          <div className="prose prose-sm prose-invert">
            {message.content}
          </div>
        </div>
        <div className="flex-shrink-0 ml-3">
          <div className="h-8 w-8 rounded-full bg-gray-300 flex items-center justify-center">
            <span className="text-white text-sm font-medium">U</span>
          </div>
        </div>
      </div>
    );
  }
  
  if (message.error) {
    return (
      <div className="flex items-start mr-auto max-w-3xl">
        <div className="flex-shrink-0 rounded-full bg-gray-100 p-2 mr-3">
          <Database className="h-5 w-5 text-emerald-600" />
        </div>
        <div className="rounded-lg bg-red-50 px-4 py-2 max-w-[85%] text-red-700">
          <p className="font-medium">Error:</p>
          <p>{message.error}</p>
        </div>
      </div>
    );
  }
  
  return (
    <div className="flex items-start mr-auto max-w-3xl">
      <div className="flex-shrink-0 rounded-full bg-gray-100 p-2 mr-3">
        <Database className="h-5 w-5 text-emerald-600" />
      </div>
      <div className="rounded-lg bg-gray-100 px-4 py-2 max-w-[85%] w-full">
        <div className="w-full">
          <div className="border-b mb-3">
            <div className="flex space-x-1">
              <button
                className={`px-3 py-2 text-sm font-medium border-b-2 ${
                  activeTab === 'results' 
                    ? 'border-emerald-600 text-emerald-600' 
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                } flex items-center gap-1 transition-colors`}
                onClick={() => setActiveTab('results')}
              >
                Results
              </button>
              <button
                className={`px-3 py-2 text-sm font-medium border-b-2 ${
                  activeTab === 'sql' 
                    ? 'border-emerald-600 text-emerald-600' 
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                } flex items-center gap-1 transition-colors`}
                onClick={() => setActiveTab('sql')}
              >
                SQL
              </button>
              <button
                className={`px-3 py-2 text-sm font-medium border-b-2 ${
                  activeTab === 'message' 
                    ? 'border-emerald-600 text-emerald-600' 
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                } flex items-center gap-1 transition-colors`}
                onClick={() => setActiveTab('message')}
              >
                Message
              </button>
            </div>
          </div>
          
          {activeTab === 'results' && (
            <div>
              {hasResults ? (
                <>
                  <div className="flex justify-between items-center mb-3">
                    <div className="relative">
                      <button 
                        onClick={() => {
                          // CSV Export function
                          const headerRow = headers.join(',');
                          const csvRows = rows.map(row => row.map(cell => 
                            // Wrap cells in quotes to handle commas in content
                            `"${cell.replace(/"/g, '""')}"`
                          ).join(','));
                          
                          const csvContent = [headerRow, ...csvRows].join('\n');
                          const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
                          const url = URL.createObjectURL(blob);
                          const link = document.createElement('a');
                          link.setAttribute('href', url);
                          link.setAttribute('download', 'query_results.csv');
                          link.style.visibility = 'hidden';
                          document.body.appendChild(link);
                          link.click();
                          document.body.removeChild(link);
                        }}
                        className="flex items-center gap-1 px-3 py-1.5 rounded-md border border-gray-300 bg-white text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-emerald-500"
                      >
                        <Download className="h-4 w-4" />
                        <span>Export CSV</span>
                      </button>
                    </div>
                  </div>
                  <div className="overflow-x-auto rounded-md border border-gray-200">
                    <table className="min-w-full divide-y divide-gray-200">
                      <thead className="bg-gray-50">
                        <tr>
                          {headers.map((header, index) => (
                            <th
                              key={index}
                              scope="col"
                              className="px-3 py-3.5 text-left text-sm font-medium text-gray-500"
                            >
                              {header}
                            </th>
                          ))}
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-gray-200 bg-white">
                        {rows.map((row, rowIndex) => (
                          <tr key={rowIndex} className="hover:bg-gray-50">
                            {row.map((cell, cellIndex) => (
                              <td
                                key={cellIndex}
                                className="whitespace-nowrap px-3 py-3 text-sm text-gray-500"
                              >
                                {cell}
                              </td>
                            ))}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                  <div className="mt-2 text-sm text-gray-500">
                    {rows.length} {rows.length === 1 ? 'row' : 'rows'}
                  </div>
                </>
              ) : (
                <div className="text-sm text-gray-600">No results available.</div>
              )}
            </div>
          )}
          
          {activeTab === 'sql' && (
            <div className="space-y-4">
              {message.sql && (
                <div>
                  <h3 className="text-sm font-medium mb-1">SQL Query</h3>
                  <div className="bg-slate-50 p-3 rounded-md border border-gray-200">
                    <pre className="text-sm font-mono whitespace-pre-wrap text-gray-800">{message.sql}</pre>
                  </div>
                </div>
              )}
              
              {message.relationalAlgebra && (
                <div>
                  <h3 className="text-sm font-medium mb-1">Relational Algebra</h3>
                  <div className="bg-slate-50 p-3 rounded-md border border-gray-200">
                    <pre className="text-sm font-mono whitespace-pre-wrap text-gray-800">{message.relationalAlgebra}</pre>
                  </div>
                </div>
              )}
            </div>
          )}
          
          {activeTab === 'message' && (
            <div className="prose prose-sm">
              {message.content}
              
              {message.llmOutput && (
                <div className="mt-3">
                  <h3 className="text-sm font-medium mb-1">LLM Processing Output</h3>
                  <div className="bg-slate-50 p-3 rounded-md border border-gray-200 max-h-40 overflow-y-auto">
                    <pre className="text-xs font-mono whitespace-pre-wrap text-gray-800">{message.llmOutput}</pre>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
