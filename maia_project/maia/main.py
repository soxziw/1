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
from typing import Dict, Any, Optional, Union, Type
import warnings
from dotenv import load_dotenv

from maia.agents import MAIA
from maia.interface import UserInterface, LLMInterface
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


def get_interface(use_llm: bool = True) -> Union[UserInterface, LLMInterface]:
    """
    Get the appropriate interface based on configuration.
    
    Args:
        use_llm: Whether to use the LLM-based interface
        
    Returns:
        An interface instance
    """
    if use_llm:
        try:
            # First check for a configured LLM provider
            return LLMInterface()
        except Exception as e:
            print(f"Warning: Failed to initialize LLM interface: {e}")
            print("Falling back to standard interface.")
            return UserInterface()
    else:
        return UserInterface()
     

def interactive_mode(use_llm: bool = True):
    """
    Run MAIA in interactive mode.
    
    Args:
        use_llm: Whether to use the LLM-based interface
    """
    # Set up the environment
    setup_environment()
    
    # Initialize the user interface
    ui = get_interface(use_llm)
    
    # Greet the user
    print(ui.greet_user())
    print("\n" + "-" * 80 + "\n")
    
    # Get the user's travel request
    user_request = input("Tell me about your travel plans: ")
    
    # Process the request
    process_request(user_request, use_llm)


def process_request(user_request: str, use_llm: bool = True) -> Dict[str, Any]:
    """
    Process a user request and generate a travel plan.
    
    Args:
        user_request: The user's travel request as a string
        use_llm: Whether to use the LLM-based interface
        
    Returns:
        Dictionary containing the travel plan
    """
    # Set up the environment
    setup_environment()
    
    # Initialize the user interface and MAIA
    ui = get_interface(use_llm)
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
    parser.add_argument("--use-llm", action="store_true", default=True,
                        help="Use LLM for improved natural language understanding (default: True)")
    parser.add_argument("--no-llm", action="store_false", dest="use_llm",
                        help="Disable LLM-based interface")
    
    args = parser.parse_args()
    
    if args.request:
        # Non-interactive mode with request provided as argument
        result = process_request(args.request, args.use_llm)
        
        # Save the result to the specified output file
        ui = get_interface(args.use_llm)
        travel_plan_path = ui.save_travel_plan(result, args.output)
        
        print(f"Travel plan saved to: {travel_plan_path}")
    else:
        # Interactive mode
        interactive_mode(args.use_llm)


if __name__ == "__main__":
    run()