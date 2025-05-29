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
    
    # Define layers in order of processing
    layers = ["area", "city", "within_city"]
    result = {
        "from_city": complete_request["from_city"],
        "destination": complete_request["destination"],
        "start_date": complete_request["start_date"],
        "end_date": complete_request["end_date"],
        "duration": complete_request["duration"],
        "total_budget": complete_request["total_budget"]
    }
    
    print("Creating your travel plan... This may take a few minutes.")
    
    issue_analysis = {}
    
    # Process each layer sequentially
    for layer in layers:
        if layer == "area":
            result["area_analysis"] = []
        elif layer == "city":
            result["city_selection"] = []
            result["intercity_transit"] = []
        elif layer == "within_city":
            result["accommodation_search"] = []
            result["activities_planning"] = []
            result["restaurant_recommendations"] = []
            result["local_transport"] = []
        
        
        print(f"Processing {layer} layer...")
        maia_system.activate_layer(layer)
        
        # Try up to two attempts for each layer
        max_attempts = 3
        current_attempt = 1
        verification_passed = False
        
        while current_attempt <= max_attempts and not verification_passed:
            # Pass the combined result from previous layers with complete_request
            layer_result = maia_system.process_request(complete_request, result, layer, issue_analysis)
            result.update(layer_result)
            
            # Verify the layer results
            verification_result = maia_system.verify_plan(layer_result, complete_request, layer)
            print(f"Verification result for {layer} layer (attempt {current_attempt}):", verification_result)
            
            # Check if verification passed
            if verification_result.get("constraints_satisfied", False):
                verification_passed = True
                issue_analysis = {}
                break
           
            # Store issues from verification result if constraints not satisfied
            detailed_analysis = verification_result["detailed_analysis"]
            # Update issues dictionary with any constraint issues found
            for constraint_type, analysis in detailed_analysis.items():
                if isinstance(analysis, dict) and not analysis.get("satisfied", True) and analysis.get("issues"):
                    issue_analysis[constraint_type] = analysis

            # If verification failed and we still have attempts left, try again
            if current_attempt < max_attempts:
                print(f"Verification failed for {layer} layer. Trying again...")
                current_attempt += 1
            else:
                print(f"Verification failed for {layer} layer after {max_attempts} attempts. Stopping processing.")
                maia_system.deactivate_layer(layer)
                return result
        
        # Update the overall result with new information from this layer
        maia_system.deactivate_layer(layer)
        print(f"Completed {layer} layer processing")
        print(f"Current travel plan after {layer} layer: {result}")
    
    print("Final result:", result)
    
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