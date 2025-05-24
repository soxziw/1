from typing import Dict, Any, List
from crewai import Agent, Crew, Task, Process
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool, ScrapeWebsiteTool
import yaml
import os
import json
from pydantic import BaseModel, Field
from typing import Optional, List

from maia.tools.travel_api_tool import (
    FlightSearchTool, 
    AccommodationSearchTool, 
    PointsOfInterestSearchTool
)
from maia.tools.constraint_validation_tool import Z3SolverTool

class AreaItem(BaseModel):
    """Pydantic model for the area item."""
    name: str
    description: str
    start_date: str
    end_date: str
    duration: int
    total_budget: float
    
class AreaAnalysis(BaseModel):
    """Pydantic model for the area analysis."""
    areas: List[AreaItem]
    
class CityItem(BaseModel):
    """Pydantic model for the city item."""
    name: str
    description: str
    start_date: str
    end_date: str
    duration: int
    total_budget: float

class CityAnalysis(BaseModel):
    """Pydantic model for the city analysis."""
    cities: List[CityItem]

class IntercityTransitItem(BaseModel):
    """Pydantic model for the intercity transit item."""
    from_city: str
    to_city: str
    mode: str
    start_time: str
    end_time: str
    duration: int
    price: float
    details: str

class IntercityTransitAnalysis(BaseModel):
    """Pydantic model for the intercity transit analysis."""
    intercity_transit: List[IntercityTransitItem]
    
class AccommodationItem(BaseModel):
    """Pydantic model for the accommodation item."""
    name: str
    location: str
    checkin_date: str
    checkout_date: str
    price: float
    rating: float
    description: str
    
class AccommodationAnalysis(BaseModel):
    """Pydantic model for the accommodation analysis."""
    accommodations: List[AccommodationItem]
    
class ActivityItem(BaseModel):
    """Pydantic model for the activity item."""
    name: str
    location: str
    date: str
    description: str
    start_time: str
    end_time: str
    duration_hours: float

class ActivitiesAnalysis(BaseModel):
    """Pydantic model for the activities analysis."""
    activities: List[ActivityItem]
    
class RestaurantItem(BaseModel):
    """Pydantic model for the restaurant item."""
    name: str
    location: str
    date: str
    time: str
    price: float
    rating: float
    description: str
    cuisine_type: str

class RestaurantAnalysis(BaseModel):
    """Pydantic model for the restaurant analysis."""
    restaurants: List[RestaurantItem]

class LocalTransportationItem(BaseModel):
    """Pydantic model for the local transportation item."""
    type: str
    from_location: str
    to_location: str
    date: str
    time: str
    price: float
    details: str
    
class LocalTransportationAnalysis(BaseModel):
    """Pydantic model for the local transportation analysis."""
    local_transportation: List[LocalTransportationItem]

class TravelPlanAreaLayer(BaseModel):
    """Pydantic model for the travel plan area analysis layer."""
    from_city: str
    destination: str
    start_date: str
    end_date: str
    duration: int
    total_budget: float
    area_analysis: AreaAnalysis

class TravelPlanCityLayer(BaseModel):
    """Pydantic model for the travel plan city selection layer."""
    from_city: str
    destination: str
    start_date: str
    end_date: str
    duration: int
    total_budget: float
    city_analysis: CityAnalysis
    
class TravelPlanWithinCityLayer(BaseModel):
    """Pydantic model for the travel plan within city layer."""
    from_city: str
    destination: str
    start_date: str
    end_date: str
    duration: int
    total_budget: float
    accommodation: AccommodationAnalysis
    activities: ActivitiesAnalysis
    restaurants: RestaurantAnalysis
    intercity_transit: IntercityTransitAnalysis
    local_transportation: LocalTransportationAnalysis

class ConstraintAnalysis(BaseModel):
    """Pydantic model for constraint analysis."""
    satisfied: bool
    issues: List[str]
    recommendations: List[str]

class MustSeeListVerification(BaseModel):
    """Pydantic model for must-see list verification."""
    satisfied: bool
    included_items: List[str]
    missing_items: List[str]
    recommendations: List[str]

class AvoidListVerification(BaseModel):
    """Pydantic model for avoid list verification."""
    satisfied: bool
    violated_items: List[str]
    recommendations: List[str]

class DetailedAnalysis(BaseModel):
    """Pydantic model for detailed verification analysis."""
    time_constraints: ConstraintAnalysis
    budget_constraints: ConstraintAnalysis
    accommodation_constraints: ConstraintAnalysis
    activity_constraints: ConstraintAnalysis
    restaurant_constraints: ConstraintAnalysis
    transportation_constraints: ConstraintAnalysis
    special_requirements: ConstraintAnalysis
    must_see_list_verification: MustSeeListVerification
    avoid_list_verification: AvoidListVerification

class VerificationResult(BaseModel):
    """Pydantic model for the plan verification result."""
    constraints_satisfied: bool
    verification_summary: str
    detailed_analysis: DetailedAnalysis

class MAIABase:
    def __init__(self):
        self.agents_config = self._load_config("agents.yaml")
        self.tasks_config = self._load_config("tasks.yaml")
        self.constraints = {}
        self.activated_agents = {
            "orchestrator": True,
            "area_analysis_specialist": False,
            "city_selection_specialist": False,
            "intercity_transit_specialist": False,
            "accommodation_search_specialist": False,
            "activities_planning_specialist": False,
            "restaurant_recommendations_specialist": False,
            "local_transport_specialist": False,
            "constraint_verification_specialist": False,
            "plan_verification_specialist": False
        }

    def _load_config(self, filename: str) -> Dict[str, Any]:
        config_path = os.path.join(os.path.dirname(__file__), "config", filename)
        with open(config_path, "r") as f:
            return yaml.safe_load(f)

    def update_constraints(self, new_constraints: Dict[str, Any]) -> None:
        self.constraints.update(new_constraints)

    def activate_agent(self, agent_name: str) -> None:
        if agent_name in self.activated_agents:
            self.activated_agents[agent_name] = True

    def activate_layer(self, layer_name: str) -> None:
        if layer_name == "area":
            self.activated_agents["area_analysis_specialist"] = True
        elif layer_name == "city":
            self.activated_agents["city_selection_specialist"] = True
            self.activated_agents["intercity_transit_specialist"] = True
        elif layer_name == "within_city":
            self.activated_agents["accommodation_search_specialist"] = True
            self.activated_agents["activities_planning_specialist"] = True
            self.activated_agents["restaurant_recommendations_specialist"] = True
            self.activated_agents["local_transport_specialist"] = True
    
    def deactivate_layer(self, layer_name: str) -> None:
        if layer_name == "area":
            self.activated_agents["area_analysis_specialist"] = False
        elif layer_name == "city":
            self.activated_agents["city_selection_specialist"] = False
            self.activated_agents["intercity_transit_specialist"] = False
        elif layer_name == "within_city":
            self.activated_agents["accommodation_search_specialist"] = False
            self.activated_agents["activities_planning_specialist"] = False
            self.activated_agents["restaurant_recommendations_specialist"] = False
            self.activated_agents["local_transport_specialist"] = False
            
@CrewBase
class MAIA(MAIABase):
    def process_request(self, complete_request: Dict[str, Any], result: Dict[str, Any], layer: str) -> Dict[str, Any]:
        result = self.crew(layer).kickoff(inputs={"travel_request": complete_request, "result": result})
        return result.to_dict()
    
    def verify_plan(self, travel_plan: Dict[str, Any], travel_request: Dict[str, Any]) -> Dict[str, Any]:
        result = self.crew_verify().kickoff(inputs={"travel_plan": travel_plan, "travel_request": travel_request})
        return result.to_dict()

    @agent
    def orchestrator(self) -> Agent:
        return Agent(
            config=self.agents_config["orchestrator"]
        )

    @task
    def request_analysis_task(self) -> Task:
        return Task(config=self.tasks_config["request_analysis_task"])

    @task
    def plan_coordination_task(self) -> Task:
        return Task(config=self.tasks_config["plan_coordination_task"])

    @task
    def area_results_merge_task(self) -> Task:
        return Task(config=self.tasks_config["area_results_merge_task"], output_json=TravelPlanAreaLayer)

    @task
    def city_results_merge_task(self) -> Task:
        return Task(config=self.tasks_config["city_results_merge_task"], output_json=TravelPlanCityLayer)

    @task
    def within_city_results_merge_task(self) -> Task:
        return Task(config=self.tasks_config["within_city_results_merge_task"], output_json=TravelPlanWithinCityLayer)

    @agent
    def area_analysis_specialist(self) -> Agent:
        return Agent(
            config=self.agents_config["area_analysis_specialist"],
            tools=[SerperDevTool(), ScrapeWebsiteTool()]
        )

    @task
    def area_analysis_task(self) -> Task:
        return Task(config=self.tasks_config["area_analysis_task"], output_json=AreaAnalysis)

    @agent
    def city_selection_specialist(self) -> Agent:
        return Agent(
            config=self.agents_config["city_selection_specialist"],
            tools=[SerperDevTool(), ScrapeWebsiteTool()]
        )

    @task
    def city_selection_task(self) -> Task:
        return Task(config=self.tasks_config["city_selection_task"], output_json=CityAnalysis)

    @agent
    def intercity_transit_specialist(self) -> Agent:
        return Agent(
            config=self.agents_config["intercity_transit_specialist"],
            tools=[SerperDevTool(), ScrapeWebsiteTool(), FlightSearchTool()]
        )

    @task
    def intercity_transit_task(self) -> Task:
        return Task(config=self.tasks_config["intercity_transit_task"], output_json=IntercityTransitAnalysis)

    @agent
    def accommodation_search_specialist(self) -> Agent:
        return Agent(
            config=self.agents_config["accommodation_search_specialist"],
            tools=[SerperDevTool(), ScrapeWebsiteTool(), AccommodationSearchTool()]
        )

    @task
    def accommodation_search_task(self) -> Task:
        return Task(config=self.tasks_config["accommodation_search_task"], output_json=AccommodationAnalysis)

    @agent
    def activities_planning_specialist(self) -> Agent:
        return Agent(
            config=self.agents_config["activities_planning_specialist"],
            tools=[SerperDevTool(), ScrapeWebsiteTool(), PointsOfInterestSearchTool()]
        )

    @task
    def activities_planning_task(self) -> Task:
        return Task(config=self.tasks_config["activities_planning_task"], output_json=ActivitiesAnalysis)

    @agent
    def restaurant_recommendations_specialist(self) -> Agent:
        return Agent(
            config=self.agents_config["restaurant_recommendations_specialist"],
            tools=[SerperDevTool(), ScrapeWebsiteTool(), PointsOfInterestSearchTool()]
        )

    @task
    def restaurant_recommendations_task(self) -> Task:
        return Task(config=self.tasks_config["restaurant_recommendations_task"], output_json=RestaurantAnalysis)

    @agent
    def local_transport_specialist(self) -> Agent:
        return Agent(
            config=self.agents_config["local_transport_specialist"],
            tools=[SerperDevTool(), ScrapeWebsiteTool()]
        )

    @task
    def local_transport_task(self) -> Task:
        return Task(config=self.tasks_config["local_transport_task"], output_json=LocalTransportationAnalysis)

    @agent
    def plan_verification_specialist(self) -> Agent:
        return Agent(
            config=self.agents_config["plan_verification_specialist"],
            tools=[Z3SolverTool()]
        )

    @task
    def plan_verification_task(self) -> Task:
        return Task(config=self.tasks_config["plan_verification_task"], output_json=VerificationResult)

    @crew
    def crew(self, layer: str) -> Crew:
        active_agents = []
        active_tasks = []

        for agent_name, is_active in self.activated_agents.items():
            if is_active:
                agent_method = getattr(self, agent_name, None)
                if callable(agent_method):
                    active_agents.append(agent_method())
                
                # Handle task names correctly for different agent types
                if agent_name == "orchestrator":
                    task_methods = [
                        self.request_analysis_task,
                        self.plan_coordination_task
                    ]
                    if layer == "area":
                        task_methods.append(self.area_results_merge_task)
                    elif layer == "city":
                        task_methods.append(self.city_results_merge_task)
                    elif layer == "within_city":
                        task_methods.append(self.within_city_results_merge_task)
                    for task_method in task_methods:
                        active_tasks.append(task_method())
                else:
                    task_name = agent_name.replace("_specialist", "") + "_task"
                    task_method = getattr(self, task_name, None)
                    if callable(task_method):
                        # Insert at the second-to-last position in active_tasks
                        active_tasks.insert(len(active_tasks) - 1, task_method())
        
        return Crew(
            agents=active_agents,
            tasks=active_tasks,
            process=Process.sequential,
            verbose=True,
            memory=False
        )
        
    def crew_verify(self) -> Crew:
        return Crew(
            agents=[self.plan_verification_specialist()],
            tasks=[self.plan_verification_task()],
            process=Process.sequential,
            verbose=True,
            memory=False
        )