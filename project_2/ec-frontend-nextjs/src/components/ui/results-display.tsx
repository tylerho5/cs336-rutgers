"use client";

import { useState } from 'react';
import { Code, TableIcon, MessageSquare, ArrowLeft } from 'lucide-react';
import { Table } from './table';

interface ResultsDisplayProps {
  originalQuery: string;
  sqlQuery: string;
  relationalAlgebra: string;
  llmOutput: string;
  results: string;
  error: string | null;
  onReset: () => void;
}

export function ResultsDisplay({
  originalQuery,
  sqlQuery,
  relationalAlgebra,
  llmOutput,
  results,
  error,
  onReset,
}: ResultsDisplayProps) {
  const [activeTab, setActiveTab] = useState<'results' | 'query' | 'llm'>('results');
  
  // Parse the results string into a table structure if possible
  const parseResults = () => {
    if (!results || error) return { headers: [], rows: [] };
    
    try {
      // Split by newlines
      const lines = results.split('\n').filter(Boolean);
      
      if (lines.length < 2) return { headers: [], rows: [] };
      
      // First line contains headers
      const headers = lines[0].split(/\s{2,}/).map(h => h.trim()).filter(Boolean);
      
      // Rest of the lines contain rows
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
  
  const { headers, rows } = parseResults();
  
  // Render appropriate error UI based on error message
  const renderErrorMessage = () => {
    if (!error) return null;
    
    // Check for different types of errors
    if (error.includes('timed out')) {
      return (
        <div className="rounded-md bg-red-50 p-4 text-red-700">
          <p className="font-medium">Request Timeout Error:</p>
          <p className="mb-2">{error}</p>
          <div className="bg-white p-3 rounded border border-red-200 mt-2">
            <p className="font-medium">Suggestions:</p>
            <ul className="list-disc pl-5 mt-1 text-sm">
              <li>Try a simpler query or break your question into smaller parts</li>
              <li>Check the server console for more information on processing status</li>
              <li>Restart the server if this happens repeatedly</li>
            </ul>
          </div>
        </div>
      );
    } else if (error.includes('connect')) {
      return (
        <div className="rounded-md bg-red-50 p-4 text-red-700">
          <p className="font-medium">Connection Error:</p>
          <p className="mb-2">{error}</p>
          <div className="bg-white p-3 rounded border border-red-200 mt-2">
            <p className="font-medium">Suggestions:</p>
            <ul className="list-disc pl-5 mt-1 text-sm">
              <li>Check that the backend server is running</li>
              <li>Verify your database credentials</li>
              <li>Restart both services with <code>./run_ec_project.sh</code></li>
            </ul>
          </div>
        </div>
      );
    } else if (error.includes('SSH') || error.includes('channel')) {
      return (
        <div className="rounded-md bg-red-50 p-4 text-red-700">
          <p className="font-medium">SSH Connection Error:</p>
          <p className="mb-2">{error}</p>
          <div className="bg-white p-3 rounded border border-red-200 mt-2">
            <p className="font-medium">Common Causes & Solutions:</p>
            <ul className="list-disc pl-5 mt-1 text-sm">
              <li><strong>Network Instability:</strong> The connection to iLab might be unstable. Try again in a moment.</li>
              <li><strong>Channel Timeout:</strong> The SSH channel might have timed out due to inactivity.</li>
              <li><strong>VPN Issues:</strong> If using a VPN, check your connection or try without it.</li>
              <li><strong>Credentials:</strong> Verify your iLab credentials and update them if needed.</li>
              <li>
                <strong>Quick Fix:</strong> Try again with the same query - the backend has been updated with automatic retry logic.
              </li>
            </ul>
          </div>
          {sqlQuery && (
            <div className="mt-4">
              <p className="font-medium">SQL Query Was Generated Successfully:</p>
              <pre className="mt-2 whitespace-pre-wrap rounded-md bg-white p-3 text-sm font-mono border border-red-200">{sqlQuery}</pre>
              <p className="mt-2 text-sm">
                You can see the generated SQL query above. The query itself is valid, but there was an error connecting to the database to execute it.
              </p>
            </div>
          )}
        </div>
      );
    } else {
      return (
        <div className="rounded-md bg-red-50 p-4 text-red-700">
          <p className="font-medium">Error:</p>
          <p>{error}</p>
        </div>
      );
    }
  };

  // Format SQL for better display
  const formatSql = (sql: string) => {
    return sql.trim();
  };
  
  return (
    <div className="w-full space-y-4 rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
      <div className="flex items-center justify-between border-b pb-4">
        <div>
          <div className="flex items-center gap-2">
            <button
              onClick={onReset}
              className="flex items-center gap-1 text-emerald-600 hover:text-emerald-800 transition-colors focus:outline-none"
            >
              <ArrowLeft className="h-4 w-4" />
              <span>New Query</span>
            </button>
          </div>
          <h3 className="mt-2 text-lg font-medium text-gray-900">
            "{originalQuery}"
          </h3>
        </div>
      </div>
      
      {error ? (
        renderErrorMessage()
      ) : (
        <>
          <div className="border-b">
            <div className="flex space-x-1">
              <button
                className={`px-4 py-3 text-sm font-medium border-b-2 ${
                  activeTab === 'results' 
                    ? 'border-emerald-600 text-emerald-600' 
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                } flex items-center gap-2 transition-colors`}
                onClick={() => setActiveTab('results')}
              >
                <TableIcon className="h-4 w-4" />
                Results
              </button>
              <button
                className={`px-4 py-3 text-sm font-medium border-b-2 ${
                  activeTab === 'query' 
                    ? 'border-emerald-600 text-emerald-600' 
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                } flex items-center gap-2 transition-colors`}
                onClick={() => setActiveTab('query')}
              >
                <Code className="h-4 w-4" />
                SQL & Relational Algebra
              </button>
              <button
                className={`px-4 py-3 text-sm font-medium border-b-2 ${
                  activeTab === 'llm' 
                    ? 'border-emerald-600 text-emerald-600' 
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                } flex items-center gap-2 transition-colors`}
                onClick={() => setActiveTab('llm')}
              >
                <MessageSquare className="h-4 w-4" />
                LLM Output
              </button>
            </div>
          </div>
          
          {activeTab === 'results' && (
            <div className="pt-2">
              <Table headers={headers} rows={rows} />
            </div>
          )}
          
          {activeTab === 'query' && (
            <div className="space-y-6 pt-4">
              <div>
                <h3 className="text-sm font-medium text-gray-900 mb-2">SQL Query</h3>
                <div className="bg-slate-50 dark:bg-slate-800 p-4 rounded-md border border-gray-200">
                  <pre className="whitespace-pre-wrap text-sm font-mono text-gray-800 dark:text-gray-200">{formatSql(sqlQuery)}</pre>
                </div>
              </div>
              
              <div>
                <h3 className="text-sm font-medium text-gray-900 mb-2">Relational Algebra</h3>
                <div className="bg-slate-50 dark:bg-slate-800 p-4 rounded-md border border-gray-200">
                  <pre className="whitespace-pre-wrap text-sm font-mono text-gray-800 dark:text-gray-200">{relationalAlgebra}</pre>
                </div>
              </div>
            </div>
          )}
          
          {activeTab === 'llm' && (
            <div className="pt-4">
              <h3 className="text-sm font-medium text-gray-900 mb-2">LLM Processing Output</h3>
              <div className="bg-slate-50 dark:bg-slate-800 p-4 rounded-md border border-gray-200 h-80 overflow-y-auto">
                <pre className="whitespace-pre-wrap text-sm text-gray-800 dark:text-gray-200">{llmOutput}</pre>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
} 