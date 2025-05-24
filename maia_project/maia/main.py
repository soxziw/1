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


def interactive_mode(ui: LLMInterface, maia_system: MAIA):
    """
    Run MAIA in interactive mode.
    
    """
    
    # Greet the user and get the travel request
    user_request = input(ui.greet_user() + "\n" + "-" * 80 + "\n" + "Tell me about your travel plans: ")
    
    # Process the request
    while 1:
        _ = process_request(ui, maia_system, user_request)
        user_request = input(ui.ask_for_updates() + "\n" + "-" * 80 + "\n" + "Provide more info or type 'done' to finish: ")
        if user_request.lower() == 'done':
            break
       
        
def process_request(ui: LLMInterface, maia_system: MAIA, user_request: str) -> Dict[str, Any]:
    """
    Process a user request and generate a travel plan.
    
    Args:
        user_request: The user's travel request as a string
        
    Returns:
        Dictionary containing the travel plan
    """
    
    print("Analyzing your request:", user_request)
    
    # Parse the user request
    parsed_request = ui.parse_user_request(user_request)
    print("Parsed request:", parsed_request)
    
    if not ui.check_required_information():
        return {}
    
    # Get any missing required information
    # complete_request = parsed_request
    complete_request = ui.complete_missing_info_suggestions()
    print("Complete request:", complete_request)
    
    # # Create constraints
    # constraints = ui.create_constraints(complete_request)
    
    # # Validate constraints
    # is_valid, validation_errors = validate_constraints(constraints)
    # if not is_valid:
    #     print("Warning: There are issues with your constraints:")
    #     for error in validation_errors:
    #         print(f"- {error}")
        
    #     # We'll continue anyway, but inform the user
    #     print("\nI'll do my best to work with these constraints, but you may want to adjust them.")
    
    # # Update MAIA's constraints
    # maia_system.update_constraints(constraints.dict())
    
    # Define layers in order of processing
    layers = ["area", "city", "within_city"]
    result = {}
    
    print("Creating your travel plan... This may take a few minutes.")
    
    # Process each layer sequentially
    for layer in layers:
        print(f"Processing {layer} layer...")
        maia_system.activate_layer(layer)
        # Pass the combined result from previous layers with complete_request
        layer_result = maia_system.process_request(complete_request, result, layer)
        
        # Verify the layer results
        verification_result = maia_system.verify_plan(layer_result, complete_request)
        print(f"Verification result for {layer} layer:", verification_result)
        
        # If verification failed, return current layer results
        if not verification_result.get("constraints_satisfied", False):
            print(f"Verification failed for {layer} layer. Stopping processing.")
            result.update(layer_result)
            maia_system.deactivate_layer(layer)
            return result
        
        # Update the overall result with new information from this layer
        result.update(layer_result)
        maia_system.deactivate_layer(layer)
        print(f"Completed {layer} layer processing")
    
    print("Result:", result)
    
    # Final verification of the complete travel plan
    verification_result = maia_system.verify_plan(result, complete_request)
    print("Final verification result:", verification_result)
    
    # # Format and save the travel plan
    # travel_plan_path = ui.save_travel_plan(result)
    
    # print(f"\nYour travel plan has been created and saved to: {travel_plan_path}")
    # print("You can open this file to view your complete itinerary.")
    
    return result


def run():
    """Main entry point function."""
    parser = argparse.ArgumentParser(description="MAIA: Multi-Agent Itinerary Assistant")
    parser.add_argument("--request", type=str, help="Travel request to process")
    parser.add_argument("--output", type=str, default="travel_plan.md",
                        help="Output file path for the travel plan")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    
    args = parser.parse_args()
    
    setup_environment()
    ui = LLMInterface()
    maia_system = MAIA()
    
    if args.request:
        # Non-interactive mode with request provided as argument
        result = process_request(ui, maia_system, args.request)
        
        # Save the result to the specified output file
        travel_plan_path = ui.save_travel_plan(result, args.output)
        
        print(f"Travel plan saved to: {travel_plan_path}")
    else:
        # Interactive mode
        interactive_mode(ui, maia_system)


if __name__ == "__main__":
    run()