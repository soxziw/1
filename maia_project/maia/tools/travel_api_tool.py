"""Tools for interacting with travel APIs."""

from crewai.tools import BaseTool
from typing import Type, Dict, Any, Optional
from pydantic import BaseModel, Field
import os
from serpapi import GoogleSearch


class FlightSearchInput(BaseModel):
    """Input schema for FlightSearchTool."""
    departure_id: str = Field(..., description="3 letter airport code of the departure location.")
    arrival_id: str = Field(..., description="3 letter airport code of the arrival location.")
    outbound_date: str = Field(..., description="Date of the outbound travel in YYYY-MM-DD format.")
    return_date: str = Field(..., description="Date of the return travel in YYYY-MM-DD format.")
    num_travelers: int = Field(1, description="Number of travelers")


class FlightSearchTool(BaseTool):
    name: str = "Flight Search Tool"
    description: str = (
        "A tool to search for flights using the SerpAPI Google Flights API. "
        "Provides detailed flight options between airports on specified dates."
    )
    args_schema: Type[BaseModel] = FlightSearchInput

    def _run(self, departure_id: str, arrival_id: str, outbound_date: str, 
             return_date: str, num_travelers: int = 1) -> str:
        """Search for flights between airports."""
        params = {
            "engine": "google_flights",
            "departure_id": departure_id,
            "arrival_id": arrival_id,
            "outbound_date": outbound_date,
            "return_date": return_date,
            "currency": "USD",
            "hl": "en",
            "api_key": os.getenv("SERPAPI_API_KEY"),
        }

        search = GoogleSearch(params)
        results = search.get_dict()
        
        # Process and format results for the agent
        return self._format_flight_results(results, num_travelers)
    
    def _format_flight_results(self, results: Dict[str, Any], num_travelers: int) -> str:
        """Format flight search results for agent consumption."""
        import json
        
        # Extract and format relevant information from results
        # This would include flight options, prices, times, etc.
        # Multiply prices by num_travelers
        
        # For now, return the full results as JSON
        return json.dumps(results)


class AccommodationSearchInput(BaseModel):
    """Input schema for AccommodationSearchTool."""
    location: str = Field(..., description="Location to search for accommodations.")
    checkin_date: str = Field(..., description="Date of the check-in in YYYY-MM-DD format.")
    checkout_date: str = Field(..., description="Date of the check-out in YYYY-MM-DD format.")
    num_travelers: int = Field(1, description="Number of travelers")
    min_rating: Optional[float] = Field(None, description="Minimum rating threshold")


class AccommodationSearchTool(BaseTool):
    name: str = "Accommodation Search Tool"
    description: str = (
        "A tool to search for accommodations using the SerpAPI Google Hotels API. "
        "Provides detailed accommodation options at a location for specified dates."
    )
    args_schema: Type[BaseModel] = AccommodationSearchInput

    def _run(self, location: str, checkin_date: str, checkout_date: str, 
             num_travelers: int = 1, min_rating: Optional[float] = None) -> str:
        """Search for accommodations at a location."""
        params = {
            "engine": "google_hotels",
            "q": f"{location} Hotels & Resorts",
            "check_in_date": checkin_date,
            "check_out_date": checkout_date,
            "adults": str(num_travelers),
            "currency": "USD",
            "gl": "us",
            "hl": "en",
            "api_key": os.getenv("SERPAPI_API_KEY"),
        }

        search = GoogleSearch(params)
        results = search.get_dict()
        
        # Process and filter results based on min_rating if provided
        return self._format_accommodation_results(results, min_rating)
    
    def _format_accommodation_results(self, results: Dict[str, Any], 
                                     min_rating: Optional[float] = None) -> str:
        """Format accommodation search results for agent consumption."""
        import json
        
        # Extract and format relevant information from results
        # Filter by min_rating if provided
        
        # For now, return the full results as JSON
        return json.dumps(results)


class PointsOfInterestSearchInput(BaseModel):
    """Input schema for PointsOfInterestSearchTool."""
    location: str = Field(..., description="Location to search for points of interest.")
    categories: Optional[str] = Field(None, description="Categories of points of interest to search for (e.g., museums, restaurants)")
    min_rating: Optional[float] = Field(None, description="Minimum rating threshold")


class PointsOfInterestSearchTool(BaseTool):
    name: str = "Points of Interest Search Tool"
    description: str = (
        "A tool to search for points of interest (attractions, restaurants, etc.) "
        "using SerpAPI. Provides detailed information about attractions at a location."
    )
    args_schema: Type[BaseModel] = PointsOfInterestSearchInput

    def _run(self, location: str, categories: Optional[str] = None, 
             min_rating: Optional[float] = None) -> str:
        """Search for points of interest at a location."""
        search_query = f"{location}"
        if categories:
            search_query += f" {categories}"
        
        params = {
            "engine": "google",
            "q": search_query,
            "tbm": "lcl",  # Local results
            "google_domain": "google.com",
            "gl": "us",
            "hl": "en",
            "api_key": os.getenv("SERPAPI_API_KEY"),
        }

        search = GoogleSearch(params)
        results = search.get_dict()
        
        # Process and filter results based on min_rating if provided
        return self._format_poi_results(results, min_rating)
    
    def _format_poi_results(self, results: Dict[str, Any], 
                           min_rating: Optional[float] = None) -> str:
        """Format points of interest search results for agent consumption."""
        import json
        
        # Extract and format relevant information from results
        # Filter by min_rating if provided
        
        # For now, return the full results as JSON
        return json.dumps(results)
