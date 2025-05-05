#!/usr/bin/env python
"""
Mock example script demonstrating how MAIA would function.
This avoids the ChromaDB dependency that causes SQLite version issues.
"""

import os
import sys
import time

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the mock MAIA processor
from mock_maia import mock_process_request


def main():
    """Run an example MAIA request."""
    # Example travel request
    request = """
    I want to plan a trip to Japan for 10 days in October 2023. I'm interested in experiencing 
    both traditional and modern Japanese culture, visiting historical sites, and trying authentic 
    Japanese cuisine. I'd like to visit Tokyo and Kyoto, and maybe one other city if time allows. 
    My budget is around $5000 excluding flights. I prefer to stay in mid-range hotels or 
    traditional ryokans. I would like to use public transportation as much as possible. 
    I'd also appreciate recommendations for some off-the-beaten-path experiences that aren't 
    too crowded with tourists. I don't speak Japanese, so language accessibility is important.
    """
    
    print("Example Request:")
    print("-" * 80)
    print(request)
    print("-" * 80)
    print()
    
    # Process the request
    try:
        # Add a small delay to simulate processing time
        print("Processing your request...")
        time.sleep(1)
        result = mock_process_request(request)
        print("Request processed successfully!")
    except Exception as e:
        print(f"Error processing request: {e}")


if __name__ == "__main__":
    main()