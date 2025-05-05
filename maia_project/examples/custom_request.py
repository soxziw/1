#!/usr/bin/env python
"""
Custom request script for MAIA.
"""

import os
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from maia.main import process_request


def main():
    """Run a custom MAIA request."""
    # Custom travel request
    request = """
    I want to plan a 10 day trip to USA from June 11 to June 21 2025. I'll be traveling 
    from New York City and I'm interested in both traditional culture and modern technology. 
    I'd like to visit San Francisco and Los Angeles. My budget is around $3000 excluding flights. 
    I prefer clean, comfortable mid-range accommodations near public transit. I'm a vegetarian 
    and enjoy walking tours.
    """
    
    print("Custom Request:")
    print("-" * 80)
    print(request)
    print("-" * 80)
    print()
    
    # Process the request
    try:
        result = process_request(request)
        print("Request processed successfully!")
        print(f"Travel plan saved to: {os.path.abspath('travel_plan.md')}")
    except Exception as e:
        print(f"Error processing request: {e}")


if __name__ == "__main__":
    main()