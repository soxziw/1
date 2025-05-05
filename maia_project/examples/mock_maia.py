#!/usr/bin/env python
"""
A simplified mock implementation of MAIA for demonstration purposes.
This avoids the ChromaDB dependency that causes SQLite version issues.
"""

import os
import sys
import json
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class MockMAIA:
    """Mock implementation of MAIA that generates a simple travel plan."""
    
    def __init__(self):
        """Initialize the mock MAIA."""
        self.constraints = {}
        
    def update_constraints(self, constraints):
        """Update the constraints for the travel plan."""
        self.constraints = constraints
        
    def activate_layer(self, layer_name):
        """Mock activation of a layer."""
        print(f"Activated {layer_name} layer")
        
    def process_user_request(self, user_request):
        """Process a user request and generate a mock travel plan."""
        print("Processing request with mock MAIA system...")
        
        # Parse the destination from the request
        if "san francisco" in user_request.lower() and "los angeles" in user_request.lower():
            destination = "USA (San Francisco and Los Angeles)"
        elif "japan" in user_request.lower():
            destination = "Japan (Tokyo and Kyoto)"
        else:
            destination = "Unknown destination"
            
        # Extract dates from constraints or use default
        start_date = self.constraints.get('start_date', '2025-06-11')
        end_date = self.constraints.get('end_date', '2025-06-21')
        duration = 10
        
        # Generate mock travel plan
        travel_plan = {
            "destination": destination,
            "start_date": start_date,
            "end_date": end_date,
            "duration": duration,
            "total_budget": self.constraints.get('total_budget', 3000),
            "itinerary": self._generate_mock_itinerary(destination, duration),
            "accommodations": self._generate_mock_accommodations(destination, duration),
            "transportation": self._generate_mock_transportation(destination)
        }
        
        return travel_plan
        
    def _generate_mock_itinerary(self, destination, duration):
        """Generate a mock itinerary based on the destination."""
        itinerary = {}
        
        if "USA" in destination:
            # San Francisco and LA itinerary
            itinerary = {
                "Day 1": [
                    "Arrive in San Francisco",
                    "Check in to hotel near Union Square",
                    "Evening walk at Fisherman's Wharf"
                ],
                "Day 2": [
                    "Golden Gate Bridge visit and photos",
                    "Explore Golden Gate Park",
                    "Lunch at a vegetarian restaurant in Haight-Ashbury",
                    "Afternoon at the California Academy of Sciences"
                ],
                "Day 3": [
                    "Morning ferry to Alcatraz Island",
                    "Lunch at the Ferry Building Marketplace",
                    "Afternoon exploring Chinatown",
                    "Cable car ride through the city"
                ],
                "Day 4": [
                    "Day trip to Silicon Valley",
                    "Visit the Computer History Museum",
                    "Tour of Stanford University campus",
                    "Evening at Castro District"
                ],
                "Day 5": [
                    "Morning at Museum of Modern Art",
                    "Lunch near Embarcadero",
                    "Afternoon flight to Los Angeles",
                    "Check in to hotel in Santa Monica"
                ],
                "Day 6": [
                    "Morning at Santa Monica Beach and Pier",
                    "Lunch at a local vegetarian café",
                    "Afternoon walking tour of Venice Beach",
                    "Evening at Third Street Promenade"
                ],
                "Day 7": [
                    "Hollywood Walk of Fame and TCL Chinese Theatre",
                    "Lunch in Hollywood",
                    "Afternoon at Griffith Observatory",
                    "Evening at Universal CityWalk"
                ],
                "Day 8": [
                    "Getty Center visit",
                    "Lunch at the museum",
                    "Afternoon shopping on Rodeo Drive",
                    "Evening at The Grove"
                ],
                "Day 9": [
                    "Day trip to Malibu",
                    "Lunch at a beachside restaurant",
                    "Afternoon at Getty Villa",
                    "Sunset at Point Dume State Beach"
                ],
                "Day 10": [
                    "Morning at LACMA",
                    "Final shopping and souvenir hunting",
                    "Farewell dinner at a vegetarian restaurant",
                    "Prepare for departure"
                ]
            }
        elif "Japan" in destination:
            # Tokyo and Kyoto itinerary
            itinerary = {
                "Day 1": [
                    "Arrive in Tokyo",
                    "Check in to hotel in Shinjuku",
                    "Evening exploration of Shinjuku area"
                ],
                "Day 2": [
                    "Visit Meiji Shrine in the morning",
                    "Explore Harajuku and Takeshita Street",
                    "Afternoon in Shibuya - see the famous crossing",
                    "Evening meal at an izakaya"
                ],
                "Day 3": [
                    "Morning at the Imperial Palace Gardens",
                    "Lunch in Ginza",
                    "Afternoon at TeamLab Planets digital art museum",
                    "Evening river cruise in Tokyo Bay"
                ],
                "Day 4": [
                    "Day trip to Nikko to see shrines and temples",
                    "Visit Toshogu Shrine",
                    "See Kegon Falls",
                    "Return to Tokyo in evening"
                ],
                "Day 5": [
                    "Morning at Tsukiji Outer Market",
                    "Lunch with fresh seafood",
                    "Afternoon at Asakusa and Senso-ji Temple",
                    "Evening in Akihabara electronic district"
                ],
                "Day 6": [
                    "Morning bullet train to Kyoto",
                    "Check in to traditional ryokan",
                    "Afternoon at Arashiyama Bamboo Grove",
                    "Evening in Gion district"
                ],
                "Day 7": [
                    "Visit Fushimi Inari Shrine early morning",
                    "Explore the thousands of torii gates",
                    "Afternoon at Kiyomizu-dera Temple",
                    "Sunset at Kiyomizu-dera viewing platform"
                ],
                "Day 8": [
                    "Morning at Kinkaku-ji (Golden Pavilion)",
                    "Lunch at a traditional restaurant",
                    "Afternoon at Nijo Castle",
                    "Evening traditional tea ceremony experience"
                ],
                "Day 9": [
                    "Day trip to Nara",
                    "Visit Todai-ji Temple and Great Buddha",
                    "Feed the sacred deer at Nara Park",
                    "Return to Kyoto in evening"
                ],
                "Day 10": [
                    "Morning at Philosopher's Path",
                    "Final shopping at Kyoto Station",
                    "Return to Tokyo by bullet train",
                    "Farewell dinner in Tokyo"
                ]
            }
        else:
            # Generic itinerary
            for day in range(1, duration + 1):
                itinerary[f"Day {day}"] = [
                    f"Morning activity in {destination}",
                    "Lunch at local restaurant",
                    "Afternoon sightseeing",
                    "Evening entertainment"
                ]
                
        return itinerary
        
    def _generate_mock_accommodations(self, destination, duration):
        """Generate mock accommodations for the trip."""
        if "USA" in destination:
            return [
                {
                    "name": "Union Square Hotel",
                    "location": "San Francisco, Union Square",
                    "price": 220,
                    "rating": 4.5,
                    "description": "Modern hotel located near public transit in Union Square",
                    "nights": 5
                },
                {
                    "name": "Santa Monica Beach Resort",
                    "location": "Los Angeles, Santa Monica",
                    "price": 245,
                    "rating": 4.3,
                    "description": "Comfortable hotel near Santa Monica Pier and public transit",
                    "nights": 5
                }
            ]
        elif "Japan" in destination:
            return [
                {
                    "name": "Shinjuku Park Hotel",
                    "location": "Tokyo, Shinjuku",
                    "price": 180,
                    "rating": 4.2,
                    "description": "Modern hotel in the heart of Tokyo near Shinjuku Station",
                    "nights": 5
                },
                {
                    "name": "Traditional Kyoto Ryokan",
                    "location": "Kyoto, Gion District",
                    "price": 210,
                    "rating": 4.7,
                    "description": "Traditional Japanese inn with tatami rooms and onsen bath",
                    "nights": 4
                },
                {
                    "name": "Tokyo Bay Hotel",
                    "location": "Tokyo, Minato",
                    "price": 150,
                    "rating": 4.0,
                    "description": "Convenient hotel for your last night near transit to airport",
                    "nights": 1
                }
            ]
        else:
            return [
                {
                    "name": "Central Hotel",
                    "location": f"{destination}, City Center",
                    "price": 150,
                    "rating": 4.0,
                    "description": "Standard hotel in a central location",
                    "nights": duration
                }
            ]
            
    def _generate_mock_transportation(self, destination):
        """Generate mock transportation options."""
        if "USA" in destination:
            return [
                {
                    "type": "Flight",
                    "from": "New York City",
                    "to": "San Francisco",
                    "date": "2025-06-11",
                    "time": "08:30",
                    "price": 350,
                    "details": "Direct flight, 6 hours"
                },
                {
                    "type": "Flight",
                    "from": "San Francisco",
                    "to": "Los Angeles",
                    "date": "2025-06-16",
                    "time": "14:15",
                    "price": 120,
                    "details": "Direct flight, 1.5 hours"
                },
                {
                    "type": "Flight",
                    "from": "Los Angeles",
                    "to": "New York City",
                    "date": "2025-06-21",
                    "time": "18:45",
                    "price": 380,
                    "details": "Direct flight, 5.5 hours"
                }
            ]
        elif "Japan" in destination:
            return [
                {
                    "type": "Flight",
                    "from": "Your Origin City",
                    "to": "Tokyo",
                    "date": "2023-10-01",
                    "time": "12:30",
                    "price": 1200,
                    "details": "International flight, 14 hours"
                },
                {
                    "type": "Bullet Train",
                    "from": "Tokyo",
                    "to": "Kyoto",
                    "date": "2023-10-06",
                    "time": "09:00",
                    "price": 140,
                    "details": "Shinkansen, 2.5 hours"
                },
                {
                    "type": "Bullet Train",
                    "from": "Kyoto",
                    "to": "Tokyo",
                    "date": "2023-10-10",
                    "time": "16:00",
                    "price": 140,
                    "details": "Shinkansen, 2.5 hours"
                },
                {
                    "type": "Flight",
                    "from": "Tokyo",
                    "to": "Your Origin City",
                    "date": "2023-10-11",
                    "time": "10:45",
                    "price": 1200,
                    "details": "International flight, 14 hours"
                }
            ]
        else:
            return [
                {
                    "type": "Flight",
                    "from": "Your Origin City",
                    "to": destination,
                    "date": "2025-06-11",
                    "time": "10:00",
                    "price": 800,
                    "details": "Round-trip flight"
                }
            ]

class MockInterface:
    """Mock implementation of UserInterface."""
    
    def parse_user_request(self, user_request):
        """Parse the user request into structured data."""
        # Very simple parsing for demonstration
        parsed_data = {
            "destination": "Unknown destination",
            "origin": "Your location",
            "start_date": "2025-06-11",
            "end_date": "2025-06-21",
            "duration": 10,
            "total_budget": 3000,
            "preferences": [],
            "constraints": [],
            "raw_request": user_request
        }
        
        # Extract destination
        if "japan" in user_request.lower():
            parsed_data["destination"] = "Japan"
            if "tokyo" in user_request.lower():
                parsed_data["destination"] += " (Tokyo)"
            if "kyoto" in user_request.lower():
                parsed_data["destination"] += " (and Kyoto)"
        elif "usa" in user_request.lower() or "united states" in user_request.lower():
            parsed_data["destination"] = "USA"
            if "san francisco" in user_request.lower():
                parsed_data["destination"] += " (San Francisco)"
            if "los angeles" in user_request.lower():
                parsed_data["destination"] += " (and Los Angeles)"
                
        # Extract budget
        import re
        budget_match = re.search(r"budget\s+(?:is|of)\s+\$?(\d+(?:,\d+)*)", user_request)
        if budget_match:
            parsed_data["total_budget"] = int(budget_match.group(1).replace(",", ""))
            
        # Extract preferences
        if "vegetarian" in user_request.lower():
            parsed_data["preferences"].append("vegetarian food")
        if "walking" in user_request.lower():
            parsed_data["preferences"].append("walking tours")
        if "culture" in user_request.lower():
            parsed_data["preferences"].append("cultural experiences")
        if "technology" in user_request.lower():
            parsed_data["preferences"].append("technology")
            
        return parsed_data
    
    def get_required_information(self, parsed_request):
        """Handle missing information in the request."""
        # Just return the parsed request for demo
        return parsed_request
    
    def create_constraints(self, parsed_request):
        """Create constraints object from the parsed request."""
        # Return a simple dict for the demo
        return parsed_request
        
    def save_travel_plan(self, plan_data, filename="travel_plan.md"):
        """Save the travel plan to a file."""
        # Format the travel plan
        formatted_plan = self._format_travel_plan(plan_data)
        
        # Save the plan to a file
        with open(filename, "w") as f:
            f.write(formatted_plan)
            
        return os.path.abspath(filename)
        
    def _format_travel_plan(self, plan_data):
        """Format the travel plan data into a Markdown document."""
        formatted_plan = (
            f"# Travel Plan for {plan_data.get('destination', 'Your Trip')}\n\n"
            f"## Overview\n\n"
            f"- **Destination:** {plan_data.get('destination', 'Not specified')}\n"
            f"- **Dates:** {plan_data.get('start_date', 'Not specified')} to "
            f"{plan_data.get('end_date', 'Not specified')}\n"
            f"- **Duration:** {plan_data.get('duration', 'Not specified')} days\n"
            f"- **Budget:** ${plan_data.get('total_budget', 'Not specified')}\n\n"
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
                    f"- **Location:** {accommodation.get('location', 'Not specified')}\n"
                    f"- **Price:** ${accommodation.get('price', 'Not specified')} per night\n"
                    f"- **Rating:** {accommodation.get('rating', 'Not specified')}/5\n"
                    f"- **Description:** {accommodation.get('description', 'Not specified')}\n"
                    f"- **Nights:** {accommodation.get('nights', 'Not specified')}\n\n"
                )
        
        # Add transportation if available
        if "transportation" in plan_data:
            formatted_plan += "## Transportation\n\n"
            
            for transport in plan_data["transportation"]:
                formatted_plan += (
                    f"### {transport.get('type', 'Transportation')} from "
                    f"{transport.get('from', 'Origin')} to "
                    f"{transport.get('to', 'Destination')}\n\n"
                    f"- **Date:** {transport.get('date', 'Not specified')}\n"
                    f"- **Time:** {transport.get('time', 'Not specified')}\n"
                    f"- **Price:** ${transport.get('price', 'Not specified')}\n"
                    f"- **Details:** {transport.get('details', 'Not specified')}\n\n"
                )
        
        return formatted_plan

def mock_process_request(user_request):
    """Process a user request with the mock MAIA system."""
    # Initialize the mock components
    interface = MockInterface()
    maia_system = MockMAIA()
    
    print("Analyzing your request...")
    
    # Parse the user request
    parsed_request = interface.parse_user_request(user_request)
    
    # Get any missing required information
    complete_request = interface.get_required_information(parsed_request)
    
    # Create constraints
    constraints = interface.create_constraints(complete_request)
    
    # Update MAIA's constraints
    maia_system.update_constraints(constraints)
    
    # Activate all layers for comprehensive planning
    maia_system.activate_layer("area")
    maia_system.activate_layer("city")
    maia_system.activate_layer("within_city")
    maia_system.activate_layer("verification")
    
    print("Creating your travel plan... This may take a few moments.")
    
    # Process the request and generate a travel plan
    result = maia_system.process_user_request(user_request)
    
    # Format and save the travel plan
    travel_plan_path = interface.save_travel_plan(result)
    
    print(f"\nYour travel plan has been created and saved to: {travel_plan_path}")
    print("You can open this file to view your complete itinerary.")
    
    return result

def main():
    """Run the mock MAIA system with a custom request."""
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
        result = mock_process_request(request)
        print("Request processed successfully!")
        print(f"Travel plan saved to: {os.path.abspath('travel_plan.md')}")
    except Exception as e:
        print(f"Error processing request: {e}")


if __name__ == "__main__":
    main()