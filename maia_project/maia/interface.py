"""
User interaction interface for MAIA.
"""

from typing import Dict, Any, Optional, List, Tuple, Union, Callable
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

# Import for LLM-based interfaces
import json
from typing import Protocol, runtime_checkable

@runtime_checkable
class LLMProvider(Protocol):
    """Protocol defining the interface for an LLM provider."""
    
    def generate_response(self, prompt: str, model: str = "gpt-4o") -> str:
        """
        Generate a response using the OpenAI GPT-4o model.
        
        Args:
            prompt: The prompt to send to the model
            model: The model to use, defaults to "gpt-4o"
            
        Returns:
            The generated response as a string
        """
        pass


class OpenAIProvider(LLMProvider):
    """Implementation of LLMProvider using OpenAI's API."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the OpenAI provider.
        
        Args:
            api_key: OpenAI API key. If None, will try to use OPENAI_API_KEY from environment
        """
        import openai
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required")
        self.client = openai.OpenAI(api_key=self.api_key)
    
    def generate_response(self, prompt: str, model: str = "gpt-4o") -> str:
        """
        Generate a response using the OpenAI API.
        
        Args:
            prompt: The prompt to send to the model
            model: The model to use, defaults to "gpt-4o"
            
        Returns:
            The generated response as a string
        """
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=2000
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error generating response from OpenAI: {e}")
            return "I'm sorry, I encountered an error while processing your request."


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
        self.complete_input = {}
        self.constraints = None
        self.travel_plan = None


class LLMInterface(UserInterface):
    """
    LLM-enhanced interface for MAIA.
    
    This class extends the basic UserInterface with LLM capabilities
    for improved natural language understanding and generation.
    """
    
    def __init__(self, llm_provider: Optional[LLMProvider] = None):
        """
        Initialize the LLM interface.
        
        Args:
            llm_provider: An object that implements the LLMProvider protocol.
                          If None, creates a default OpenAIProvider.
        """
        super().__init__()
        if llm_provider is None:
            self.llm = OpenAIProvider()
        else:
            self.llm = llm_provider

    def parse_user_request(self, user_request: str) -> Dict[str, Any]:
        """
        Parse the user's natural language request into structured data using LLM.
        
        Args:
            user_request: The user's travel request as a string
            
        Returns:
            Dictionary containing parsed information
        """
        # Define the prompt for the LLM
        prompt = f"""
        Update based on the following travel information I've collected:
            {json.dumps(self.user_input, indent=2)}
        Please extract travel planning information from the following user request.
        Format your response as a JSON object with the following fields:
        
        - destination: The destination(s) the user wants to visit
        - origin: Where the user is traveling from (if mentioned)
        - start_date: The start date of the trip (in YYYY-MM-DD format)
        - end_date: The end date of the trip (in YYYY-MM-DD format)
        - duration: The number of days of the trip
        - total_budget: The total budget for the trip (as a number without currency symbol)
        - accommodation_types: A list of preferred accommodation types 
        - cuisine_preferences: A list of food or cuisine preferences
        - activity_preferences: A list of preferred activities or interests
        - accessibility_requirements: Any accessibility needs
        - avoid_list: A list of things the user wants to avoid
        - must_see_list: A list of must-see attractions or experiences
        - travel_pace: The preferred pace of travel (relaxed, moderate, fast)
        - transportation_preferences: Preferred modes of transportation
        - num_travelers: The number of people traveling
        - special_occasions: Any special occasions being celebrated
        - language_requirements: Any language preferences or requirements
        - custom_constraints: Any other specific constraints or requirements
        
        User request:
        {user_request}
        
        JSON response:
        """
        
        # Get LLM response
        response = self.llm.generate_response(prompt)
        
        # Extract the JSON part from the response (in case LLM included extra text)
        json_start = response.find('{')
        json_end = response.rfind('}') + 1
        if json_start != -1 and json_end != -1:
            json_str = response[json_start:json_end]
            parsed_data = json.loads(json_str)
        
        self.user_input = parsed_data
        return parsed_data
    
    def check_required_information(self) -> bool:
        # Check for required fields
        required_fields = ["destination", "total_budget"]
        required_time_info = ["start_date", "end_date", "duration"]
        
        # Check for empty or missing fields
        missing_fields = []
        for field in required_fields:
            if not self.user_input.get(field):
                missing_fields.append(field)
        
        # Check for time information
        has_time_info = any(self.user_input.get(field) for field in required_time_info)
        if not has_time_info:
            missing_fields.append("travel_dates")
            
        # If no missing fields, return as is
        if not missing_fields:
            return True
        
        return False
        
    def complete_missing_info_suggestions(self) -> Dict[str, Any]:
        """
        Identify missing information and suggest values for all empty fields.
            
        Returns:
            Updated dictionary with suggested values for all empty fields
        """
        parsed_data = self.user_input
        
        # Define all possible fields that could be in a complete travel request
        all_fields = [
            "destination", "origin", "start_date", "end_date", "duration", 
            "total_budget", "accommodation_types", "cuisine_preferences",
            "activity_preferences", "accessibility_requirements", "avoid_list",
            "must_see_list", "travel_pace", "transportation_preferences",
            "num_travelers", "special_occasions", "language_requirements",
            "custom_constraints"
        ]
        
        # Check for empty or missing fields
        missing_fields = []
        for field in all_fields:
            if not self.user_input.get(field):
                missing_fields.append(field)
        
        # If no missing fields, return as is
        if not missing_fields:
            self.complete_input = self.user_input
            return self.user_input
        
        # Use LLM to suggest values for missing fields
        prompt = f"""
        Based on the following partial travel request information:
        {json.dumps(self.user_input, indent=2)}
        
        Please suggest reasonable default values for ALL the following missing fields:
        {", ".join(missing_fields)}
        
        Consider any contextual clues in the provided information to make your suggestions as relevant as possible.
        
        For reference, here are all the fields that could be included in a complete travel request:
        - destination: The destination(s) the user wants to visit
        - origin: Where the user is traveling from (if mentioned)
        - start_date: The start date of the trip (in YYYY-MM-DD format)
        - end_date: The end date of the trip (in YYYY-MM-DD format)
        - duration: The number of days of the trip
        - total_budget: The total budget for the trip (as a number without currency symbol)
        - accommodation_types: A list of preferred accommodation types 
        - cuisine_preferences: A list of food or cuisine preferences
        - activity_preferences: A list of preferred activities or interests
        - accessibility_requirements: Any accessibility needs
        - avoid_list: A list of things the user wants to avoid
        - must_see_list: A list of must-see attractions or experiences
        - travel_pace: The preferred pace of travel (relaxed, moderate, fast)
        - transportation_preferences: Preferred modes of transportation
        - num_travelers: The number of people traveling
        - special_occasions: Any special occasions being celebrated
        - language_requirements: Any language preferences or requirements
        - custom_constraints: Any other specific constraints or requirements
        
        Format your response as a JSON object with ONLY the missing fields and their suggested values.
        """
        
        # Get LLM response
        response = self.llm.generate_response(prompt)
        
        # Parse the JSON response
        # Extract the JSON part from the response
        json_start = response.find('{')
        json_end = response.rfind('}') + 1
        if json_start != -1 and json_end != -1:
            json_str = response[json_start:json_end]
            suggested_values = json.loads(json_str)
            
            # Update the parsed request with suggested values
            updated_request = self.user_input.copy()
            updated_request.update(suggested_values)
        
        self.complete_input = updated_request
        return updated_request
        
    def greet_user(self) -> str:
        """
        Generate a personalized greeting message for the user using LLM.
        
        Returns:
            Greeting message string
        """
        # Use LLM to generate a more personalized greeting
        prompt = """
        Create a friendly and engaging greeting message for a travel planning assistant called MAIA 
        (Multi-Agent Itinerary Assistant). The message should:
        
        1. Introduce MAIA and explain its purpose (creating personalized travel itineraries)
        2. Mention that MAIA uses advanced AI to understand user preferences and constraints
        3. Ask users to provide details about their travel plans including:
           - Destination interests
           - Travel dates and duration
           - Budget considerations
           - Accommodation preferences
           - Activity interests
           - Restaurant preferences
           - Transportation preferences
           - Any special requirements or constraints
        4. Encourage users to provide as much detail as possible for better results
        5. Be welcoming, conversational, and enthusiastic about helping plan their trip
        
        Keep the greeting concise but informative. Format it with appropriate spacing and bullet points.
        """
        
        try:
            # Get LLM response
            response = self.llm.generate_response(prompt)
            
            # If we got a valid response, use it
            if response and len(response.strip()) > 100:  # Minimum length check
                return response
        except Exception as e:
            print(f"Error generating greeting with LLM: {e}")
        
        # Fallback to default greeting
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
    
    def ask_for_updates(self) -> str:
        """
        Ask the user for additional information or updates to their travel plan.
        
        Returns:
            A prompt asking for additional information or updates
        """
        # Determine what information might still be useful to collect
        missing_or_incomplete = []
        
        # Check if we have user input to analyze
        if self.user_input:
            # Check for required fields
            required_fields = ["destination", "total_budget"]
            required_time_info = ["start_date", "end_date", "duration"]
            
            # Check for empty or missing fields
            missing_fields = []
            for field in required_fields:
                if not self.user_input.get(field):
                    missing_fields.append(field)
            
            # Check for time information
            has_time_info = any(self.user_input.get(field) for field in required_time_info)
            if not has_time_info:
                missing_fields.append("travel_dates")
            
            # Add required fields to missing_or_incomplete
            missing_or_incomplete.extend(missing_fields)
            
            # Check for other useful but non-required fields
            if not self.user_input.get('activity_preferences'):
                missing_or_incomplete.append("activities or interests")
            if not self.user_input.get('accommodation_types'):
                missing_or_incomplete.append("accommodation preferences")
            if not self.user_input.get('cuisine_preferences'):
                missing_or_incomplete.append("food or restaurant preferences")
            if not self.user_input.get('travel_pace'):
                missing_or_incomplete.append("preferred travel pace (relaxed, moderate, or fast-paced)")
        
        # Create a prompt for the LLM based on what we know
        prompt = ""
        if self.complete_input:
            # We have complete input, so ask for refinements
            prompt = f"""
            Based on the following travel information I've collected:
            {json.dumps(self.complete_input, indent=2)}
            
            Create a friendly message asking the user if they want to:
            1. Add any additional details to their travel plan
            2. Modify any of the current details
            3. Confirm the information is correct
            
            If there are specific areas that seem incomplete (like {', '.join(missing_or_incomplete) if missing_or_incomplete else 'any preferences or special requirements'}), 
            gently prompt for those details specifically.
            
            Keep the message conversational, helpful, and concise.
            """
        else:
            # We don't have complete input yet, so ask for basic information
            prompt = """
            Create a friendly message asking the user to provide more details about their travel plans.
            Suggest they might want to include information about:
            - Activities they enjoy or specific attractions they want to see
            - Accommodation preferences (luxury, budget, etc.)
            - Restaurant preferences or dietary restrictions
            - Transportation preferences
            - Any special requirements or constraints
            
            Keep the message conversational, helpful, and concise.
            """
        
        if self.complete_input:
            self.user_input = self.complete_input
            
        try:
            # Get LLM response
            response = self.llm.generate_response(prompt)
            
            # If we got a valid response, use it
            if response and len(response.strip()) > 50:  # Minimum length check
                return response
        except Exception as e:
            print(f"Error generating follow-up prompt with LLM: {e}")
        
        # Fallback to default prompt
        if missing_or_incomplete:
            return (
                f"Thanks for that information! To create an even better travel plan, "
                f"could you tell me more about your {', '.join(missing_or_incomplete)}?\n\n"
                f"Or if you have any other details to add or modify, please let me know."
            )
        else:
            return (
                "Thank you for the information! Is there anything else you'd like to add or modify "
                "about your travel plans? Any specific preferences or requirements I should know about?\n\n"
                "The more details you provide, the better I can tailor your travel experience."
            )
    
    
    def extract_constraints_with_llm(self, parsed_request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract detailed travel constraints using LLM.
        
        Args:
            parsed_request: Dictionary containing the parsed request
            
        Returns:
            Enhanced dictionary with detailed constraints
        """
        # Format a prompt that asks the LLM to extract detailed constraints
        prompt = f"""
        Based on the following travel request information:
        {json.dumps(parsed_request, indent=2)}
        
        Please extract and infer detailed travel constraints and preferences.
        Format your response as a JSON object with the following structure:
        
        {{
          "time": {{
            "start_date": "YYYY-MM-DD",
            "end_date": "YYYY-MM-DD",
            "min_days_per_city": number,
            "max_days_per_city": number,
            "earliest_departure_time": "HH:MM",
            "latest_departure_time": "HH:MM",
            "earliest_activity_time": "HH:MM",
            "latest_activity_time": "HH:MM"
          }},
          "budget": {{
            "total_budget": number,
            "accommodation_budget_per_night": number,
            "food_budget_per_day": number,
            "activity_budget_per_day": number,
            "transportation_budget": number,
            "currency": "USD"
          }},
          "preferences": {{
            "accommodation_types": [list of strings],
            "cuisine_preferences": [list of strings],
            "activity_preferences": [list of strings],
            "accessibility_requirements": [list of strings],
            "avoid_list": [list of strings],
            "must_see_list": [list of strings],
            "travel_pace": "relaxed/moderate/fast",
            "rating_threshold": number
          }},
          "destination": "string",
          "origin": "string",
          "num_travelers": number,
          "custom_constraints": {{ any additional constraints }}
        }}
        
        Infer reasonable values for any fields not explicitly mentioned in the request,
        based on the context and typical travel patterns. If information cannot be 
        reasonably inferred, use null for numeric values and empty arrays for lists.
        """
        
        # Get LLM response
        response = self.llm.generate_response(prompt)
        
        # Parse the JSON response
        try:
            # Extract the JSON part from the response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start != -1 and json_end != -1:
                json_str = response[json_start:json_end]
                constraints_data = json.loads(json_str)
                
                # Return the enhanced constraints
                return constraints_data
            else:
                # If we can't extract JSON, just return the original request
                return parsed_request
        except json.JSONDecodeError:
            # If JSON parsing fails, return the original request
            return parsed_request
            
    def create_constraints(self, parsed_request: Dict[str, Any]) -> Constraints:
        """
        Create a constraints object from the parsed request using LLM.
        
        Args:
            parsed_request: Dictionary containing the parsed request
            
        Returns:
            Constraints object
        """
        # First extract detailed constraints using LLM
        enhanced_data = self.extract_constraints_with_llm(parsed_request)
        
        try:
            # Create TimeConstraint
            time_data = enhanced_data.get("time", {})
            time_constraint = TimeConstraint(
                start_date=time_data.get("start_date") or parsed_request.get("start_date", "2023-06-01"),
                end_date=time_data.get("end_date") or parsed_request.get("end_date", "2023-06-10"),
                min_days_per_city=time_data.get("min_days_per_city", 1),
                max_days_per_city=time_data.get("max_days_per_city", 5),
                earliest_departure_time=time_data.get("earliest_departure_time", "08:00"),
                latest_departure_time=time_data.get("latest_departure_time", "21:00"),
                earliest_activity_time=time_data.get("earliest_activity_time", "08:00"),
                latest_activity_time=time_data.get("latest_activity_time", "22:00")
            )
            
            # Create BudgetConstraint
            budget_data = enhanced_data.get("budget", {})
            budget_constraint = BudgetConstraint(
                total_budget=budget_data.get("total_budget") or parsed_request.get("total_budget", 3000),
                accommodation_budget_per_night=budget_data.get("accommodation_budget_per_night"),
                food_budget_per_day=budget_data.get("food_budget_per_day"),
                activity_budget_per_day=budget_data.get("activity_budget_per_day"),
                transportation_budget=budget_data.get("transportation_budget"),
                currency=budget_data.get("currency", "USD")
            )
            
            # Create PreferenceConstraint
            pref_data = enhanced_data.get("preferences", {})
            preference_constraint = PreferenceConstraint(
                accommodation_types=pref_data.get("accommodation_types", []),
                cuisine_preferences=pref_data.get("cuisine_preferences", []),
                activity_preferences=pref_data.get("activity_preferences", []),
                accessibility_requirements=pref_data.get("accessibility_requirements", []),
                avoid_list=pref_data.get("avoid_list", []),
                must_see_list=pref_data.get("must_see_list", []),
                travel_pace=pref_data.get("travel_pace", "moderate"),
                rating_threshold=pref_data.get("rating_threshold", 4.0)
            )
            
            # Create Constraints
            constraints = Constraints(
                time=time_constraint,
                budget=budget_constraint,
                preferences=preference_constraint,
                destination=enhanced_data.get("destination") or parsed_request.get("destination", ""),
                origin=enhanced_data.get("origin") or parsed_request.get("origin", ""),
                num_travelers=enhanced_data.get("num_travelers") or parsed_request.get("num_travelers", 1),
                custom_constraints=enhanced_data.get("custom_constraints", {})
            )
            
            # Validate constraints
            is_valid, validation_errors = validate_constraints(constraints)
            if not is_valid:
                print(f"Warning: Generated constraints have validation errors: {validation_errors}")
            
            self.constraints = constraints
            return constraints
            
        except Exception as e:
            # If something goes wrong, fall back to the original method
            print(f"Error creating constraints with LLM: {e}")
            return super().create_constraints(parsed_request)
    
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
