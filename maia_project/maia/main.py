#!/usr/bin/env python
"""
Main entry point for MAIA: Multi-Agent Itinerary Assistant.

This module provides the main functionality for running MAIA as a
command-line application or importing it as a module.
"""

import argparse
import json
import os
import sys
from typing import Dict, Any, Optional
import warnings
from dotenv import load_dotenv

from maia.agents import MAIA
from maia.interface import UserInterface
from maia.constraints import validate_constraints


def setup_environment():
    """Set up the environment variables and configuration."""
    # Load environment variables from .env file
    load_dotenv()
    
    # Suppress warnings
    warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")
    
    # Check for required API keys
    required_keys = ["OPENAI_API_KEY", "SERPAPI_API_KEY"]
    missing_keys = [key for key in required_keys if not os.getenv(key)]
    
    if missing_keys:
        print("Error: The following required API keys are missing:")
        for key in missing_keys:
            print(f"- {key}")
        print("\nPlease add these keys to your .env file.")
        sys.exit(1)


def interactive_mode():
    """Run MAIA in interactive mode."""
    # Set up the environment
    setup_environment()
    
    # Initialize the user interface
    ui = UserInterface()
    
    # Greet the user
    print(ui.greet_user())
    print("\n" + "-" * 80 + "\n")
    
    # Get the user's travel request
    user_request = input("Tell me about your travel plans: ")
    
    # Process the request
    process_request(user_request)


def process_request(user_request: str) -> Dict[str, Any]:
    """
    Process a user request and generate a travel plan.
    
    Args:
        user_request: The user's travel request as a string
        
    Returns:
        Dictionary containing the travel plan
    """
    # Set up the environment
    setup_environment()
    
    # Initialize the user interface and MAIA
    ui = UserInterface()
    maia_system = MAIA()
    
    print("Analyzing your request...")
    
    # Parse the user request
    parsed_request = ui.parse_user_request(user_request)
    
    # Get any missing required information
    complete_request = ui.get_required_information(parsed_request)
    
    # Create constraints
    constraints = ui.create_constraints(complete_request)
    
    # Validate constraints
    is_valid, validation_errors = validate_constraints(constraints)
    if not is_valid:
        print("Warning: There are issues with your constraints:")
        for error in validation_errors:
            print(f"- {error}")
        
        # We'll continue anyway, but inform the user
        print("\nI'll do my best to work with these constraints, but you may want to adjust them.")
    
    # Update MAIA's constraints
    maia_system.update_constraints(constraints.dict())
    
    # Activate all layers for comprehensive planning
    maia_system.activate_layer("area")
    maia_system.activate_layer("city")
    maia_system.activate_layer("within_city")
    maia_system.activate_layer("verification")
    
    print("Creating your travel plan... This may take a few minutes.")
    
    # Process the request and generate a travel plan
    result = maia_system.process_user_request(user_request)
    
    # Format and save the travel plan
    travel_plan_path = ui.save_travel_plan(result)
    
    print(f"\nYour travel plan has been created and saved to: {travel_plan_path}")
    print("You can open this file to view your complete itinerary.")
    
    return result


def run():
    """Main entry point function."""
    parser = argparse.ArgumentParser(description="MAIA: Multi-Agent Itinerary Assistant")
    parser.add_argument("--request", type=str, help="Travel request to process")
    parser.add_argument("--output", type=str, default="travel_plan.md",
                        help="Output file path for the travel plan")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    
    args = parser.parse_args()
    
    if args.request:
        # Non-interactive mode with request provided as argument
        result = process_request(args.request)
        
        # Save the result to the specified output file
        ui = UserInterface()
        travel_plan_path = ui.save_travel_plan(result, args.output)
        
        print(f"Travel plan saved to: {travel_plan_path}")
    else:
        # Interactive mode
        interactive_mode()


if __name__ == "__main__":
    run()