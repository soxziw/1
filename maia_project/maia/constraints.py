"""Constraint handling module for MAIA."""
from typing import Dict, Any, List, Tuple, Optional
from pydantic import BaseModel, Field


class TimeConstraint(BaseModel):
    """Time-related constraints."""
    start_date: Optional[str] = Field(None, description="Start date of the trip (YYYY-MM-DD)")
    end_date: Optional[str] = Field(None, description="End date of the trip (YYYY-MM-DD)")
    min_days_per_city: Optional[int] = Field(None, description="Minimum days to spend in each city")
    max_days_per_city: Optional[int] = Field(None, description="Maximum days to spend in each city")
    earliest_departure_time: Optional[str] = Field(None, description="Earliest departure time for travel")
    latest_departure_time: Optional[str] = Field(None, description="Latest departure time for travel")
    earliest_activity_time: Optional[str] = Field(None, description="Earliest time for activities to start")
    latest_activity_time: Optional[str] = Field(None, description="Latest time for activities to end")


class BudgetConstraint(BaseModel):
    """Budget-related constraints."""
    total_budget: Optional[float] = Field(None, description="Total budget for the trip")
    accommodation_budget_per_night: Optional[float] = Field(None, description="Maximum budget for accommodation per night")
    food_budget_per_day: Optional[float] = Field(None, description="Maximum budget for food per day")
    activity_budget_per_day: Optional[float] = Field(None, description="Maximum budget for activities per day")
    transportation_budget: Optional[float] = Field(None, description="Maximum budget for transportation")
    currency: Optional[str] = Field(None, description="Currency for all budget values")


class PreferenceConstraint(BaseModel):
    """User preference constraints."""
    accommodation_types: Optional[List[str]] = Field(None, description="Preferred accommodation types")
    cuisine_preferences: Optional[List[str]] = Field(None, description="Preferred cuisines")
    activity_preferences: Optional[List[str]] = Field(None, description="Preferred activity types")
    accessibility_requirements: Optional[List[str]] = Field(None, description="Accessibility requirements")
    avoid_list: Optional[List[str]] = Field(None, description="Things to avoid")
    must_see_list: Optional[List[str]] = Field(None, description="Must-see attractions/experiences")
    travel_pace: Optional[str] = Field(None, description="Preferred travel pace (relaxed, moderate, fast)")
    rating_threshold: Optional[float] = Field(None, description="Minimum rating threshold for recommendations")


class Constraints(BaseModel):
    """Complete set of constraints for trip planning."""
    time: Optional[TimeConstraint] = Field(None)
    budget: Optional[BudgetConstraint] = Field(None)
    preferences: Optional[PreferenceConstraint] = Field(None)
    destination: Optional[str] = Field(None, description="Destination for the trip")
    origin: Optional[str] = Field(None, description="Origin location for the trip")
    num_travelers: Optional[int] = Field(None, description="Number of travelers")
    custom_constraints: Optional[Dict[str, Any]] = Field(None, description="Custom constraints")


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
    if constraints.time:
        time = constraints.time
        if time.min_days_per_city and time.max_days_per_city and time.min_days_per_city > time.max_days_per_city:
            is_valid = False
            validation_errors.append("Minimum days per city cannot exceed maximum days per city")
    
    # Validate budget constraints
    if constraints.budget:
        budget = constraints.budget
        if budget.total_budget:
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
    time_constraint = TimeConstraint(
        start_date=user_input.get("start_date"),
        end_date=user_input.get("end_date"),
        min_days_per_city=user_input.get("min_days_per_city", 1),
        max_days_per_city=user_input.get("max_days_per_city"),
        earliest_departure_time=user_input.get("earliest_departure_time"),
        latest_departure_time=user_input.get("latest_departure_time"),
        earliest_activity_time=user_input.get("earliest_activity_time"),
        latest_activity_time=user_input.get("latest_activity_time")
    )
    
    budget_constraint = BudgetConstraint(
        total_budget=user_input.get("total_budget"),
        accommodation_budget_per_night=user_input.get("accommodation_budget"),
        food_budget_per_day=user_input.get("food_budget"),
        activity_budget_per_day=user_input.get("activity_budget"),
        transportation_budget=user_input.get("transportation_budget"),
        currency=user_input.get("currency", "USD")
    )
    
    preference_constraint = PreferenceConstraint(
        accommodation_types=user_input.get("accommodation_types"),
        cuisine_preferences=user_input.get("cuisine_preferences"),
        activity_preferences=user_input.get("activity_preferences"),
        accessibility_requirements=user_input.get("accessibility_requirements"),
        avoid_list=user_input.get("avoid_list"),
        must_see_list=user_input.get("must_see_list"),
        travel_pace=user_input.get("travel_pace"),
        rating_threshold=user_input.get("rating_threshold", 4.0)
    )
    
    return Constraints(
        time=time_constraint,
        budget=budget_constraint,
        preferences=preference_constraint,
        destination=user_input.get("destination"),
        origin=user_input.get("origin"),
        num_travelers=user_input.get("num_travelers", 1),
        custom_constraints=user_input.get("custom_constraints")
    )
