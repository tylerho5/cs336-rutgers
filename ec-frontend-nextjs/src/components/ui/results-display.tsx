"use client";

import { useState } from 'react';

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
  const [activeTab, setActiveTab] = useState<'query' | 'llm' | 'results'>('results');
  
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
  
  // Function to sort rows by a column
  const [sortColumn, setSortColumn] = useState<number | null>(null);
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('asc');
  
  const handleSort = (columnIndex: number) => {
    if (sortColumn === columnIndex) {
      // Toggle direction if same column
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      // New column, default to ascending
      setSortColumn(columnIndex);
      setSortDirection('asc');
    }
  };
  
  // Sort the rows if a sort column is selected
  const sortedRows = [...rows];
  if (sortColumn !== null && sortColumn < headers.length) {
    sortedRows.sort((a, b) => {
      const valA = a[sortColumn] || '';
      const valB = b[sortColumn] || '';
      
      // Try numeric comparison first
      const numA = Number(valA);
      const numB = Number(valB);
      
      if (!isNaN(numA) && !isNaN(numB)) {
        return sortDirection === 'asc' ? numA - numB : numB - numA;
      }
      
      // Fall back to string comparison
      return sortDirection === 'asc' 
        ? valA.localeCompare(valB)
        : valB.localeCompare(valA);
    });
  }
  
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
  
  return (
    <div className="w-full space-y-4 rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-medium">Query Results</h2>
        <button
          onClick={onReset}
          className="rounded-md bg-gray-100 px-3 py-1.5 text-sm font-medium text-gray-600 hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-gray-400"
        >
          New Query
        </button>
      </div>
      
      {error ? (
        renderErrorMessage()
      ) : (
        <>
          <div className="overflow-hidden rounded-md border border-gray-200">
            <div className="flex border-b border-gray-200">
              <button
                className={`px-4 py-2 text-sm font-medium ${
                  activeTab === 'results' ? 'bg-gray-100 text-blue-600' : 'text-gray-600 hover:bg-gray-50'
                }`}
                onClick={() => setActiveTab('results')}
              >
                Results
              </button>
              <button
                className={`px-4 py-2 text-sm font-medium ${
                  activeTab === 'query' ? 'bg-gray-100 text-blue-600' : 'text-gray-600 hover:bg-gray-50'
                }`}
                onClick={() => setActiveTab('query')}
              >
                SQL Query
              </button>
              <button
                className={`px-4 py-2 text-sm font-medium ${
                  activeTab === 'llm' ? 'bg-gray-100 text-blue-600' : 'text-gray-600 hover:bg-gray-50'
                }`}
                onClick={() => setActiveTab('llm')}
              >
                LLM Output
              </button>
            </div>
            
            <div className="p-4">
              {activeTab === 'results' && (
                <div>
                  <div className="mb-2">
                    <p><strong>Original Question:</strong> {originalQuery}</p>
                  </div>
                  {headers.length > 0 ? (
                    <div className="overflow-x-auto">
                      <table className="min-w-full divide-y divide-gray-200">
                        <thead className="bg-gray-50">
                          <tr>
                            {headers.map((header, index) => (
                              <th
                                key={index}
                                scope="col"
                                className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500 cursor-pointer"
                                onClick={() => handleSort(index)}
                              >
                                {header}
                                {sortColumn === index && (
                                  <span className="ml-1">
                                    {sortDirection === 'asc' ? '↑' : '↓'}
                                  </span>
                                )}
                              </th>
                            ))}
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-200 bg-white">
                          {sortedRows.map((row, rowIndex) => (
                            <tr key={rowIndex} className={rowIndex % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                              {row.map((cell, cellIndex) => (
                                <td
                                  key={cellIndex}
                                  className="whitespace-nowrap px-6 py-4 text-sm text-gray-500"
                                >
                                  {cell}
                                </td>
                              ))}
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  ) : (
                    <pre className="mt-2 whitespace-pre-wrap rounded-md bg-gray-50 p-4 text-sm font-mono">
                      {results || 'No results to display'}
                    </pre>
                  )}
                </div>
              )}
              
              {activeTab === 'query' && (
                <div>
                  <div className="mb-4">
                    <h3 className="text-sm font-medium text-gray-700">Relational Algebra:</h3>
                    <pre className="mt-2 whitespace-pre-wrap rounded-md bg-gray-50 p-4 text-sm font-mono">
                      {relationalAlgebra || 'No relational algebra available'}
                    </pre>
                  </div>
                  <div>
                    <h3 className="text-sm font-medium text-gray-700">SQL Query:</h3>
                    <pre className="mt-2 whitespace-pre-wrap rounded-md bg-gray-50 p-4 text-sm font-mono">
                      {sqlQuery || 'No SQL query available'}
                    </pre>
                  </div>
                </div>
              )}
              
              {activeTab === 'llm' && (
                <div>
                  <h3 className="text-sm font-medium text-gray-700">LLM Processing Output:</h3>
                  <pre className="mt-2 whitespace-pre-wrap rounded-md bg-gray-50 p-4 text-sm font-mono">
                    {llmOutput || 'No LLM output available'}
                  </pre>
                </div>
              )}
            </div>
          </div>
        </>
      )}
    </div>
  );
} 