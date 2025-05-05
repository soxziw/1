"""
User interaction interface for MAIA.
"""

from typing import Dict, Any, Optional, List, Tuple
import json
import re
import os
from datetime import datetime

from maia.constraints import (
    TimeConstraint,
    BudgetConstraint,
    PreferenceConstraint,
    Constraints,
    parse_user_input_to_constraints,
    validate_constraints
)


class UserInterface:
    """
    User interface for MAIA.
    
    This class provides methods for interacting with users,
    collecting travel preferences and constraints, and displaying
    travel plans.
    """
    
    def __init__(self):
        """Initialize the user interface."""
        self.user_input = {}
        self.constraints = None
        self.travel_plan = None
    
    def greet_user(self) -> str:
        """
        Generate a greeting message for the user.
        
        Returns:
            Greeting message string
        """
        return (
            "Welcome to MAIA (Multi-Agent Itinerary Assistant)!\n\n"
            "I'm here to help you plan your perfect trip by understanding your travel "
            "preferences and constraints. I'll create a detailed itinerary that strictly "
            "adheres to your requirements.\n\n"
            "To get started, please tell me about your travel plans. Include information "
            "about:\n"
            "- Where you want to go\n"
            "- When you want to travel and for how long\n"
            "- Your budget\n"
            "- Your interests and preferences\n"
            "- Any specific constraints or requirements\n\n"
            "The more details you provide, the better I can tailor your travel plan!"
        )
    
    def parse_user_request(self, user_request: str) -> Dict[str, Any]:
        """
        Parse the user's natural language request into structured data.
        
        Args:
            user_request: The user's travel request as a string
            
        Returns:
            Dictionary containing parsed information
        """
        # This is where we would use LLM-based extraction to parse the request
        # For now, we'll use a simple regex-based approach for demonstration
        
        # Extract destination
        destination_match = re.search(r"to\s+([A-Za-z\s,]+)", user_request)
        destination = destination_match.group(1).strip() if destination_match else ""
        
        # Extract dates or duration
        date_match = re.search(r"from\s+(\w+\s+\d+)\s+to\s+(\w+\s+\d+)", user_request)
        duration_match = re.search(r"for\s+(\d+)\s+(days|weeks)", user_request)
        
        start_date = ""
        end_date = ""
        duration = 0
        
        if date_match:
            start_date_str = date_match.group(1)
            end_date_str = date_match.group(2)
            
            # Convert to proper date format
            try:
                start_date = datetime.strptime(
                    f"{start_date_str} {datetime.now().year}", "%B %d %Y"
                ).strftime("%Y-%m-%d")
                
                end_date = datetime.strptime(
                    f"{end_date_str} {datetime.now().year}", "%B %d %Y"
                ).strftime("%Y-%m-%d")
            except ValueError:
                # Handle date parsing errors
                pass
        elif duration_match:
            duration_value = int(duration_match.group(1))
            duration_unit = duration_match.group(2)
            
            if duration_unit == "weeks":
                duration = duration_value * 7
            else:
                duration = duration_value
        
        # Extract budget
        budget_match = re.search(r"budget\s+of\s+\\?\\$?(\d+(?:,\d+)*(?:\.\d+)?)", user_request)
        budget = float(budget_match.group(1).replace(",", "")) if budget_match else 0
        
        # Extract origin
        origin_match = re.search(r"from\s+([A-Za-z\s,]+)\s+to", user_request)
        origin = origin_match.group(1).strip() if origin_match else ""
        
        # Extract preferences
        preferences = []
        interest_keywords = [
            "interested in", "enjoy", "like", "love", "prefer",
            "museums", "beaches", "mountains", "hiking", "food",
            "culture", "history", "nature", "shopping", "nightlife"
        ]
        
        for keyword in interest_keywords:
            if keyword in user_request.lower():
                if keyword not in ["interested in", "enjoy", "like", "love", "prefer"]:
                    preferences.append(keyword)
        
        # Extract constraints
        constraints = []
        constraint_keywords = [
            "must", "need", "require", "only", "avoid", "wheelchair",
            "accessible", "allergic", "allergy", "vegetarian", "vegan",
            "gluten-free", "pet-friendly", "family-friendly", "budget-friendly"
        ]
        
        for keyword in constraint_keywords:
            if keyword in user_request.lower():
                constraints.append(keyword)
        
        # Create structured data
        parsed_data = {
            "destination": destination,
            "origin": origin,
            "start_date": start_date,
            "end_date": end_date,
            "duration": duration,
            "total_budget": budget,
            "preferences": preferences,
            "constraints": constraints,
            "raw_request": user_request
        }
        
        self.user_input = parsed_data
        return parsed_data
    
    def get_required_information(self, parsed_request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Identify missing required information and prompt the user.
        
        Args:
            parsed_request: Dictionary containing the parsed request
            
        Returns:
            Updated dictionary with all required information
        """
        required_fields = ["destination", "total_budget"]
        required_time_info = ["start_date", "end_date", "duration"]
        
        # Check for required fields
        missing_fields = []
        for field in required_fields:
            if not parsed_request.get(field):
                missing_fields.append(field)
        
        # Check for time information
        has_time_info = any(parsed_request.get(field) for field in required_time_info)
        if not has_time_info:
            missing_fields.append("travel_dates")
        
        if not missing_fields:
            return parsed_request
        
        # This is where we would prompt the user for missing information
        # For now, just add placeholder values
        updated_request = parsed_request.copy()
        
        if "destination" in missing_fields:
            updated_request["destination"] = "Paris, France"
        
        if "total_budget" in missing_fields:
            updated_request["total_budget"] = 3000.0
        
        if "travel_dates" in missing_fields:
            updated_request["start_date"] = "2023-07-01"
            updated_request["end_date"] = "2023-07-10"
        
        self.user_input = updated_request
        return updated_request
    
    def create_constraints(self, parsed_request: Dict[str, Any]) -> Constraints:
        """
        Create a constraints object from the parsed request.
        
        Args:
            parsed_request: Dictionary containing the parsed request
            
        Returns:
            Constraints object
        """
        constraints = parse_user_input_to_constraints(parsed_request)
        self.constraints = constraints
        return constraints
    
    def format_travel_plan(self, plan_data: Dict[str, Any]) -> str:
        """
        Format the travel plan data into a user-friendly display.
        
        Args:
            plan_data: Dictionary containing the travel plan data
            
        Returns:
            Formatted travel plan string
        """
        # This is where we would format the travel plan into a nice display
        # For now, just convert the data to a formatted string
        formatted_plan = (
            f"# Travel Plan for {plan_data.get('destination', 'Your Trip')}\n\n"
            f"## Overview\n\n"
            f"Destination: {plan_data.get('destination', 'Not specified')}\n"
            f"Dates: {plan_data.get('start_date', 'Not specified')} to "
            f"{plan_data.get('end_date', 'Not specified')}\n"
            f"Duration: {plan_data.get('duration', 'Not specified')} days\n"
            f"Budget: ${plan_data.get('total_budget', 'Not specified')}\n\n"
        )
        
        # Add itinerary if available
        if "itinerary" in plan_data:
            formatted_plan += "## Itinerary\n\n"
            
            for day, activities in plan_data["itinerary"].items():
                formatted_plan += f"### {day}\n\n"
                
                for activity in activities:
                    formatted_plan += f"- {activity}\n"
                
                formatted_plan += "\n"
        
        # Add accommodations if available
        if "accommodations" in plan_data:
            formatted_plan += "## Accommodations\n\n"
            
            for accommodation in plan_data["accommodations"]:
                formatted_plan += (
                    f"### {accommodation.get('name', 'Accommodation')}\n\n"
                    f"- Location: {accommodation.get('location', 'Not specified')}\n"
                    f"- Price: ${accommodation.get('price', 'Not specified')} per night\n"
                    f"- Rating: {accommodation.get('rating', 'Not specified')}/5\n"
                    f"- Description: {accommodation.get('description', 'Not specified')}\n\n"
                )
        
        # Add transportation if available
        if "transportation" in plan_data:
            formatted_plan += "## Transportation\n\n"
            
            for transport in plan_data["transportation"]:
                formatted_plan += (
                    f"### {transport.get('type', 'Transportation')} from "
                    f"{transport.get('from', 'Origin')} to "
                    f"{transport.get('to', 'Destination')}\n\n"
                    f"- Date: {transport.get('date', 'Not specified')}\n"
                    f"- Time: {transport.get('time', 'Not specified')}\n"
                    f"- Price: ${transport.get('price', 'Not specified')}\n"
                    f"- Details: {transport.get('details', 'Not specified')}\n\n"
                )
        
        return formatted_plan
    
    def save_travel_plan(self, plan_data: Dict[str, Any], filename: str = "travel_plan.md") -> str:
        """
        Save the travel plan to a file.
        
        Args:
            plan_data: Dictionary containing the travel plan data
            filename: Name of the file to save the plan to
            
        Returns:
            Path to the saved file
        """
        formatted_plan = self.format_travel_plan(plan_data)
        
        with open(filename, "w") as f:
            f.write(formatted_plan)
        
        return os.path.abspath(filename)
    
    def get_feedback(self, travel_plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get feedback from the user on the travel plan.
        
        Args:
            travel_plan: Dictionary containing the travel plan
            
        Returns:
            Dictionary containing the user's feedback
        """
        # This is where we would collect feedback from the user
        # For now, just return a placeholder
        return {
            "satisfaction": 5,  # 1-5 scale
            "comments": "Great plan!",
            "suggestions": []
        }