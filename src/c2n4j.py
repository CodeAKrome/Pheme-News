#!/usr/bin/env python3

import sys
import argparse
from neo4j import GraphDatabase
from neo4j.exceptions import Neo4jError
import os
from tqdm import tqdm

PASS = os.environ.get('NEO4J_PASSWORD')
URI = os.environ.get('NEO4J_URI')
USER = 'neo4j'

BAR_RES = False

if not URI or not PASS:
    print("Error: NEO4J_URI and NEO4J_PASSWORD environment variables must be set.", file=sys.stderr)
    sys.exit(1)
    
class Neo4jQueryExecutor:
    def __init__(self, uri, username, password):
        self.driver = GraphDatabase.driver(uri, auth=(username, password))
    
    def close(self):
        self.driver.close()
    
    def execute_query(self, query):
        """Execute a single Cypher query and return results"""
        try:
            with self.driver.session() as session:
                result = session.run(query)
                records = list(result)
                summary = result.consume()
                return records, summary
        except Neo4jError as e:
            return None, str(e)
    
    def format_results(self, records, summary):
        """Format query results for display"""
        if not records:
            # No records returned - show summary info
            counters = summary.counters
            if any([counters.nodes_created, counters.nodes_deleted, 
                   counters.relationships_created, counters.relationships_deleted,
                   counters.properties_set]):
                return f"Query completed: {counters}"
            return "Query completed (no results)"
        
        output = []
        
        # Display column headers
        headers = list(records[0].keys())
        output.append(" | ".join(headers))
        output.append("-" * len(" | ".join(headers)))
        
        # Display record data
        for record in records:
            row = []
            for key in headers:
                value = record[key]
                if value is None:
                    row.append("NULL")
                else:
                    row.append(str(value))
            output.append(" | ".join(row))
        
        # Add record count
        output.append(f"\n{len(records)} record(s) returned")
        
        return "\n".join(output)


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Execute Cypher queries from stdin against Neo4j database",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  echo "MATCH (n) RETURN count(n)" | python %(prog)s bolt://localhost:7687 neo4j password
  cat queries.txt | python %(prog)s neo4j://localhost:7687 username password
  python %(prog)s bolt://localhost:7687 neo4j password < queries.cypher
        """
    )
    parser.add_argument(
        "--continue-on-error", "-c",
        action="store_true",
        help="Continue executing queries even if one fails"
    )
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Only output query results, suppress status messages"
    )
    parser.add_argument(
        "--no-progress", "-n",
        action="store_true",
        help="Disable progress bar"
    )
    
    return parser.parse_args()


def read_queries_from_stdin():
    """Read Cypher queries from stdin, one per line"""
    queries = []
    
    for line_num, line in enumerate(sys.stdin, 1):
        query = line.strip()
        if query and not query.startswith('#'):  # Skip empty lines and comments
            queries.append((line_num, query))
    
    return queries


def main():
    args = parse_arguments()
    
    # Create Neo4j connection
    try:
        print(f"Trying to connect to Neo4j at {URI} as user {USER}", file=sys.stderr)
        executor = Neo4jQueryExecutor(URI, USER, PASS)
        if not args.quiet:
            print(f"Connected to Neo4j at {URI} as user {USER}", file=sys.stderr)
    except Exception as e:
        print(f"Failed to connect to Neo4j: {e}", file=sys.stderr)
        sys.exit(1)
    
    try:
        # Read queries from stdin
        queries = read_queries_from_stdin()
        
        if not queries:
            print("No queries found in stdin", file=sys.stderr)
            sys.exit(1)
        
        if not args.quiet:
            print(f"Executing {len(queries)} queries...\n")
        
        # Set up progress bar if multiple queries and not disabled
        show_progress = len(queries) > 1 and not args.no_progress and not args.quiet
        progress_bar = None
        
        if show_progress:
            progress_bar = tqdm(
                total=len(queries),
                desc="Executing queries",
                unit="query",
                file=sys.stderr,
                leave=True
            )
        
        # Execute each query
        failed_count = 0
        for line_num, query in queries:
            if not args.quiet and not show_progress:
                # Only show individual query info if not using progress bar
                print(f"--- Line {line_num} ---")
                print(f"Query: {query}")
            
            # Update progress bar description with current query info
            if progress_bar:
                progress_bar.set_description(f"Executing query {line_num}")
            
            records, summary_or_error = executor.execute_query(query)
            
            if records is None:  # Error occurred
                failed_count += 1
                if progress_bar:
                    progress_bar.write(f"ERROR (line {line_num}): {summary_or_error}")
                else:
                    print(f"ERROR (line {line_num}): {summary_or_error}", file=sys.stderr)
                
                if not args.continue_on_error:
                    if progress_bar:
                        progress_bar.close()
                    print("Stopping execution. Use --continue-on-error to continue on errors.", file=sys.stderr)
                    break
            else:
                if BAR_RES:
                    # Format and display results
                    formatted_results = executor.format_results(records, summary_or_error)
                    if progress_bar:
                        progress_bar.write(formatted_results)
                    else:
                        print(formatted_results)
            
            # Update progress bar
            if progress_bar:
                progress_bar.update(1)
            elif not args.quiet and len(queries) > 1:
                print()  # Add spacing between queries
        
        # Close progress bar
        if progress_bar:
            progress_bar.close()
        
        # Final summary
        if not args.quiet:
            successful_count = len(queries) - failed_count
            print(f"\nExecution complete: {successful_count} successful, {failed_count} failed")
    
    except KeyboardInterrupt:
        if progress_bar:
            progress_bar.close()
        print("\nExecution interrupted by user", file=sys.stderr)
        sys.exit(130)
    except BrokenPipeError:
        # Handle broken pipe gracefully (e.g., when piping to head)
        if progress_bar:
            progress_bar.close()
        sys.exit(0)
    except Exception as e:
        if progress_bar:
            progress_bar.close()
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        executor.close()


if __name__ == "__main__":
    main()
