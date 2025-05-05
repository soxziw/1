"""Constraint handling module for MAIA."""
from typing import Dict, Any, List, Tuple
from pydantic import BaseModel, Field


class TimeConstraint(BaseModel):
    """Time-related constraints."""
    start_date: str = Field(..., description="Start date of the trip (YYYY-MM-DD)")
    end_date: str = Field(..., description="End date of the trip (YYYY-MM-DD)")
    min_days_per_city: int = Field(1, description="Minimum days to spend in each city")
    max_days_per_city: int = Field(7, description="Maximum days to spend in each city")
    earliest_departure_time: str = Field("00:00", description="Earliest departure time for travel")
    latest_departure_time: str = Field("23:59", description="Latest departure time for travel")
    earliest_activity_time: str = Field("08:00", description="Earliest time for activities to start")
    latest_activity_time: str = Field("22:00", description="Latest time for activities to end")


class BudgetConstraint(BaseModel):
    """Budget-related constraints."""
    total_budget: float = Field(..., description="Total budget for the trip")
    accommodation_budget_per_night: float = Field(None, description="Maximum budget for accommodation per night")
    food_budget_per_day: float = Field(None, description="Maximum budget for food per day")
    activity_budget_per_day: float = Field(None, description="Maximum budget for activities per day")
    transportation_budget: float = Field(None, description="Maximum budget for transportation")
    currency: str = Field("USD", description="Currency for all budget values")


class PreferenceConstraint(BaseModel):
    """User preference constraints."""
    accommodation_types: List[str] = Field([], description="Preferred accommodation types")
    cuisine_preferences: List[str] = Field([], description="Preferred cuisines")
    activity_preferences: List[str] = Field([], description="Preferred activity types")
    accessibility_requirements: List[str] = Field([], description="Accessibility requirements")
    avoid_list: List[str] = Field([], description="Things to avoid")
    must_see_list: List[str] = Field([], description="Must-see attractions/experiences")
    travel_pace: str = Field("moderate", description="Preferred travel pace (relaxed, moderate, fast)")
    rating_threshold: float = Field(4.0, description="Minimum rating threshold for recommendations")


class Constraints(BaseModel):
    """Complete set of constraints for trip planning."""
    time: TimeConstraint = Field(...)
    budget: BudgetConstraint = Field(...)
    preferences: PreferenceConstraint = Field(default_factory=PreferenceConstraint)
    destination: str = Field(..., description="Destination for the trip")
    origin: str = Field(..., description="Origin location for the trip")
    num_travelers: int = Field(1, description="Number of travelers")
    custom_constraints: Dict[str, Any] = Field(default_factory=dict, description="Custom constraints")


def validate_constraints(constraints: Constraints) -> Tuple[bool, List[str]]:
    """Validate that constraints are internally consistent.
    
    Args:
        constraints: The constraints to validate
        
    Returns:
        Tuple of (is_valid, list_of_validation_errors)
    """
    is_valid = True
    validation_errors = []
    
    # Validate time constraints
    time = constraints.time
    if time.min_days_per_city > time.max_days_per_city:
        is_valid = False
        validation_errors.append("Minimum days per city cannot exceed maximum days per city")
    
    # Validate budget constraints
    budget = constraints.budget
    budget_allocations = [
        budget.accommodation_budget_per_night,
        budget.food_budget_per_day,
        budget.activity_budget_per_day,
        budget.transportation_budget
    ]
    specified_allocations = [b for b in budget_allocations if b is not None]
    
    if specified_allocations and sum(specified_allocations) > budget.total_budget:
        is_valid = False
        validation_errors.append("The sum of budget allocations exceeds the total budget")
    
    return is_valid, validation_errors


def parse_user_input_to_constraints(user_input: Dict[str, Any]) -> Constraints:
    """Parse user input into structured constraints.
    
    Args:
        user_input: Dictionary of user input
        
    Returns:
        Structured constraints object
    """
    # This would be implemented with a mix of direct mapping and LLM extraction
    # For now, we'll just create a simple example
    time_constraint = TimeConstraint(
        start_date=user_input.get("start_date", "2023-06-01"),
        end_date=user_input.get("end_date", "2023-06-10"),
        min_days_per_city=user_input.get("min_days_per_city", 1),
        max_days_per_city=user_input.get("max_days_per_city", 5),
        earliest_departure_time=user_input.get("earliest_departure_time", "08:00"),
        latest_departure_time=user_input.get("latest_departure_time", "21:00"),
        earliest_activity_time=user_input.get("earliest_activity_time", "08:00"),
        latest_activity_time=user_input.get("latest_activity_time", "22:00")
    )
    
    budget_constraint = BudgetConstraint(
        total_budget=user_input.get("total_budget", 3000),
        accommodation_budget_per_night=user_input.get("accommodation_budget", None),
        food_budget_per_day=user_input.get("food_budget", None),
        activity_budget_per_day=user_input.get("activity_budget", None),
        transportation_budget=user_input.get("transportation_budget", None),
        currency=user_input.get("currency", "USD")
    )
    
    preference_constraint = PreferenceConstraint(
        accommodation_types=user_input.get("accommodation_types", []),
        cuisine_preferences=user_input.get("cuisine_preferences", []),
        activity_preferences=user_input.get("activity_preferences", []),
        accessibility_requirements=user_input.get("accessibility_requirements", []),
        avoid_list=user_input.get("avoid_list", []),
        must_see_list=user_input.get("must_see_list", []),
        travel_pace=user_input.get("travel_pace", "moderate"),
        rating_threshold=user_input.get("rating_threshold", 4.0)
    )
    
    return Constraints(
        time=time_constraint,
        budget=budget_constraint,
        preferences=preference_constraint,
        destination=user_input.get("destination", ""),
        origin=user_input.get("origin", ""),
        num_travelers=user_input.get("num_travelers", 1),
        custom_constraints=user_input.get("custom_constraints", {})
    )
