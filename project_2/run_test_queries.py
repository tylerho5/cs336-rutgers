#!/usr/bin/env python3

import os
import subprocess
import re
import time

# Extract actual queries from test_querys.txt
def extract_queries(file_path):
    queries = []
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Extract queries, which follow a number and description format
    pattern = r'\d+\.\s+.*?:\s+"(.*?)"'
    matches = re.findall(pattern, content, re.DOTALL)
    
    for match in matches:
        queries.append(match.strip())
    
    return queries

# Run a single query and save the output
def run_query(query, output_dir, query_num):
    print(f"\n{'='*80}")
    print(f"Running Query #{query_num}: {query}")
    print(f"{'='*80}\n")
    
    # Create the command that feeds the query into the database_llm.py
    # Use bash explicitly and the correct paths
    command = f'''bash -c 'cd /home/admiralx/cs336-rutgers/project_2 && 
                source /home/admiralx/cs336-rutgers/project_2/CS336P2/bin/activate && 
                printf "{query}\\nexit\\n" | 
                KMP_DUPLICATE_LIB_OK=TRUE python3 database_llm.py' '''
    
    # Run the command and capture output
    start_time = time.time()
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    end_time = time.time()
    
    # Save output to file
    result_file = os.path.join(output_dir, f"query_{query_num}_result.txt")
    with open(result_file, 'w') as f:
        f.write(f"Query #{query_num}: {query}\n")
        f.write(f"{'='*80}\n\n")
        f.write(f"STDOUT:\n{stdout.decode('utf-8')}\n\n")
        
        if stderr:
            f.write(f"STDERR:\n{stderr.decode('utf-8')}\n\n")
        
        f.write(f"Execution time: {end_time - start_time:.2f} seconds\n")
    
    print(f"Results saved to {result_file}")
    
    # Return a brief summary
    return {
        "query_num": query_num,
        "query": query,
        "execution_time": end_time - start_time,
        "success": process.returncode == 0
    }

def main():
    # Path to test queries file
    test_queries_path = "project_2/test_querys.txt"
    
    # Create output directory for results
    output_dir = "project_2/test_results"
    os.makedirs(output_dir, exist_ok=True)
    
    # Extract queries
    queries = extract_queries(test_queries_path)
    
    # Summary of results
    results = []
    
    # Run each query
    for i, query in enumerate(queries, 1):
        result = run_query(query, output_dir, i)
        results.append(result)
        
        # Sleep a bit to give the system time between queries
        if i < len(queries):
            print("\nWaiting 2 seconds before next query...\n")
            time.sleep(2)
    
    # Write summary report
    summary_file = os.path.join(output_dir, "summary.txt")
    with open(summary_file, 'w') as f:
        f.write("Test Queries Summary Report\n")
        f.write("==========================\n\n")
        
        f.write(f"Total Queries: {len(results)}\n")
        successful_queries = sum(1 for r in results if r["success"])
        f.write(f"Successful Queries: {successful_queries}\n")
        f.write(f"Failed Queries: {len(results) - successful_queries}\n\n")
        
        f.write("Query Details:\n")
        for r in results:
            f.write(f"#{r['query_num']} - {'Success' if r['success'] else 'Failed'} - {r['execution_time']:.2f}s - {r['query'][:60]}{'...' if len(r['query']) > 60 else ''}\n")
    
    print(f"\nTest complete! Summary saved to {summary_file}")

if __name__ == "__main__":
    main() 