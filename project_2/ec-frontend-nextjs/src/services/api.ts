interface QueryResult {
  original_query: string;
  sql_query: string;
  relational_algebra: string;
  llm_output: string;
  results: string;
  error: string | null;
}

export async function submitQuery(query: string): Promise<QueryResult> {
  try {
    // Add a timeout to the fetch request
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 300000); // 5 minutes timeout (300000ms)
    
    const response = await fetch('http://localhost:8000/api/query', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ query }),
      signal: controller.signal
    });
    
    clearTimeout(timeoutId);

    if (!response.ok) {
      let errorMessage = 'Failed to process query';
      try {
        const errorData = await response.json();
        errorMessage = errorData.detail || errorMessage;
      } catch {
        // If we can't parse the error response, use the status text
        errorMessage = `Error ${response.status}: ${response.statusText || errorMessage}`;
      }
      throw new Error(errorMessage);
    }

    return await response.json();
  } catch (error) {
    console.error('Error submitting query:', error);
    
    let errorMessage = 'An unknown error occurred';
    
    if (error instanceof Error) {
      if (error.name === 'AbortError') {
        errorMessage = 'Request timed out after 5 minutes. The operation may be taking too long.';
      } else if (error.message.includes('Failed to fetch')) {
        errorMessage = 'Could not connect to the backend server. Please ensure it is running.';
      } else {
        errorMessage = error.message;
      }
    }
    
    return {
      original_query: query,
      sql_query: '',
      relational_algebra: '',
      llm_output: '',
      results: '',
      error: errorMessage,
    };
  }
} 