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

class NextAgent(BaseModel):
    """Pydantic model for the next agent."""
    next_agent: str

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
    items: List[AreaItem]
    
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
    items: List[CityItem]

class IntercityTransitSegmentItem(BaseModel):
    """Pydantic model for the intercity transit segment."""
    from_city: str
    to_city: str
    start_date: str
    end_date: str
    mode:str
    budget: float

class IntercityTransitSegment(BaseModel):
    """Pydantic model for the intercity transit segment."""
    segments: List[IntercityTransitSegmentItem]

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
    items: List[IntercityTransitItem]
    
class AccommodationSearchSegmentItem(BaseModel):
    """Pydantic model for the accommodation search segment."""
    city: str
    start_date: str
    end_date: str
    budget_per_night: float

class AccommodationSearchSegment(BaseModel):
    """Pydantic model for the accommodation search segment."""
    segments: List[AccommodationSearchSegmentItem]

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
    items: List[AccommodationItem]
    
class ActivitiesPlanningSegmentItem(BaseModel):
    """Pydantic model for the activities planning segment."""
    city: str
    start_date: str
    end_date: str
    budget: float

class ActivitiesPlanningSegment(BaseModel):
    """Pydantic model for the activities planning segment."""
    segments: List[ActivitiesPlanningSegmentItem]

class ActivityItem(BaseModel):
    """Pydantic model for the activity item."""
    name: str
    location: str
    date: str
    description: str
    start_time: str
    end_time: str
    duration_hours: float
    price: float
    
class ActivitiesAnalysis(BaseModel):
    """Pydantic model for the activities analysis."""
    items: List[ActivityItem]
    
class RestaurantSegmentItem(BaseModel):
    """Pydantic model for the restaurant segment."""
    city: str
    start_date: str
    end_date: str
    budget_per_meal: float

class RestaurantSegment(BaseModel):
    """Pydantic model for the restaurant segment."""
    segments: List[RestaurantSegmentItem]

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
    items: List[RestaurantItem]

class LocalTransportationSegmentItem(BaseModel):
    """Pydantic model for the local transportation segment."""
    from_location: str
    to_location: str
    start_date: str
    end_date: str
    mode: str
    budget: float

class LocalTransportationSegment(BaseModel):
    """Pydantic model for the local transportation segment."""
    segments: List[LocalTransportationSegmentItem]

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
    items: List[LocalTransportationItem]

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
    city_analysis: Optional[CityAnalysis] = None
    intercity_transit: Optional[IntercityTransitAnalysis] = None
    
class TravelPlanWithinCityLayer(BaseModel):
    """Pydantic model for the travel plan within city layer."""
    from_city: str
    destination: str
    start_date: str
    end_date: str
    duration: int
    total_budget: float
    intercity_transit: IntercityTransitAnalysis
    accommodation: Optional[AccommodationAnalysis] = None
    activities: Optional[ActivitiesAnalysis] = None
    restaurants: Optional[RestaurantAnalysis] = None
    local_transportation: Optional[LocalTransportationAnalysis] = None

class ConstraintAnalysis(BaseModel):
    """Pydantic model for constraint analysis."""
    satisfied: bool
    issues: List[str]
    recommendations: List[str]

class LengthOfFieldVerification(BaseModel):
    """Pydantic model for length of field verification."""
    satisfied: bool
    length_of_field_list: int
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

class AreaDetailedAnalysis(BaseModel):
    """Pydantic model for area detailed verification analysis."""
    from_city_constraints: ConstraintAnalysis
    destination_constraints: ConstraintAnalysis
    time_constraints: ConstraintAnalysis
    budget_constraints: ConstraintAnalysis
    length_of_area_constraints: LengthOfFieldVerification
    area_constraints: ConstraintAnalysis
    
class CityDetailedAnalysis(BaseModel):
    """Pydantic model for city detailed verification analysis."""
    from_city_constraints: ConstraintAnalysis
    destination_constraints: ConstraintAnalysis
    time_constraints: ConstraintAnalysis
    budget_constraints: ConstraintAnalysis
    length_of_city_constraints: LengthOfFieldVerification
    length_of_city_constraints: LengthOfFieldVerification
    length_of_intercity_transit_constraints: LengthOfFieldVerification
    area_constraints: ConstraintAnalysis
    city_selection_constraints: ConstraintAnalysis
    intercity_transit_constraints: ConstraintAnalysis
    
class WithinCityDetailedAnalysis(BaseModel):
    """Pydantic model for within city detailed verification analysis."""
    from_city_constraints: ConstraintAnalysis
    destination_constraints: ConstraintAnalysis
    time_constraints: ConstraintAnalysis
    budget_constraints: ConstraintAnalysis
    length_of_area_constraints: LengthOfFieldVerification
    length_of_city_constraints: LengthOfFieldVerification
    length_of_intercity_transit_constraints: LengthOfFieldVerification
    length_of_accommodation_constraints: LengthOfFieldVerification
    length_of_activity_constraints: LengthOfFieldVerification
    length_of_restaurant_constraints: LengthOfFieldVerification
    length_of_local_transportation_constraints: LengthOfFieldVerification
    area_constraints: ConstraintAnalysis
    city_selection_constraints: ConstraintAnalysis
    intercity_transit_constraints: ConstraintAnalysis
    accommodation_constraints: ConstraintAnalysis
    activity_constraints: ConstraintAnalysis
    restaurant_constraints: ConstraintAnalysis
    local_transportation_constraints: ConstraintAnalysis
    special_requirements: ConstraintAnalysis
    must_see_list_verification: MustSeeListVerification
    avoid_list_verification: AvoidListVerification

class AreaVerificationResult(BaseModel):
    """Pydantic model for the plan verification result."""
    constraints_satisfied: bool
    verification_summary: str
    detailed_analysis: AreaDetailedAnalysis

class CityVerificationResult(BaseModel):
    """Pydantic model for the plan verification result."""
    constraints_satisfied: bool
    verification_summary: str
    detailed_analysis: CityDetailedAnalysis

class WithinCityVerificationResult(BaseModel):
    """Pydantic model for the plan verification result."""
    constraints_satisfied: bool
    verification_summary: str
    detailed_analysis: WithinCityDetailedAnalysis

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
    def process_request(self, complete_request: Dict[str, Any], result: Dict[str, Any], layer: str, issue_analysis: Dict[str, Any]) -> Dict[str, Any]:
        current_result = result.copy()
        while True:
            layer_dict = {
                "area": {"area_analysis_specialist": self.agents_config["area_analysis_specialist"]},
                "city": {"city_selection_specialist": self.agents_config["city_selection_specialist"],
                         "intercity_transit_specialist": self.agents_config["intercity_transit_specialist"]},
                "within_city": {"accommodation_search_specialist": self.agents_config["accommodation_search_specialist"], 
                                "activities_planning_specialist": self.agents_config["activities_planning_specialist"], 
                                "restaurant_recommendations_specialist": self.agents_config["restaurant_recommendations_specialist"], 
                                "local_transport_specialist": self.agents_config["local_transport_specialist"]}
            }
            # Determine what task to run next
            next_agent_result = self.crew_plan_next().kickoff(
                inputs={"travel_request": complete_request, "result": current_result, "agents": layer_dict[layer], "issue_analysis": issue_analysis}
            )
            
            next_agent = next_agent_result.to_dict().get("next_agent", "none")
            print(f"Next agent: {next_agent}")
            
            # If no more tasks to run, we're done
            if next_agent == "none":
                break
            
            subtasks = [{}]
            if next_agent != "area_analysis_specialist" and next_agent != "city_selection_specialist":
                split_result = self.crew_split_task(next_agent).kickoff(
                    inputs={"travel_request": complete_request, "result": current_result}
                )
                subtasks = split_result.to_dict().get("segments", [])
            
            print(f"Subtasks: {subtasks}")
            
            task_results = []
            for subtask in subtasks:
                # If split task fails or doesn't exist, run the regular task
                task_result = self.crew_run_task(next_agent).kickoff(
                    inputs={"travel_request": complete_request, "result": current_result, "segment": subtask}
                )
                print(f"Task result: {task_result}")
                # Merge task results into the main result
                task_results = task_results + task_result.to_dict().get("items", [])
            
            agent_key = next_agent.replace("_specialist", "")
            current_result.update({agent_key: task_results})
            
            print(f"Current result: {current_result}")
        return current_result
    
    def verify_plan(self, travel_plan: Dict[str, Any], travel_request: Dict[str, Any], layer: str) -> Dict[str, Any]:
        component_name = {
            "area": ["area"],
            "city": ["cities", "intercity transit"],
            "within_city": ["accommodations", "activities", "restaurants", "local transportation"]
        }
        result = self.crew_verify(layer).kickoff(inputs={"travel_plan": travel_plan, "travel_request": travel_request, "component_name": component_name[layer]})
        return result.to_dict()

    @agent
    def orchestrator(self) -> Agent:
        return Agent(
            config=self.agents_config["orchestrator"]
        )

    @task
    def plan_next_task(self) -> Task:
        return Task(config=self.tasks_config["plan_next_task"], output_json=NextAgent)

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
    def intercity_transit_split_task(self) -> Task:
        return Task(config=self.tasks_config["intercity_transit_split_task"], output_json=IntercityTransitSegment)

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
    def accommodation_search_split_task(self) -> Task:
        return Task(config=self.tasks_config["accommodation_search_split_task"], output_json=AccommodationSearchSegment)

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
    def activities_planning_split_task(self) -> Task:
        return Task(config=self.tasks_config["activities_planning_split_task"], output_json=ActivitiesPlanningSegment)

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
    def restaurant_recommendations_split_task(self) -> Task:
        return Task(config=self.tasks_config["restaurant_recommendations_split_task"], output_json=RestaurantSegment)

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
    def local_transport_split_task(self) -> Task:
        return Task(config=self.tasks_config["local_transport_split_task"], output_json=LocalTransportationSegment)

    @task
    def local_transport_task(self) -> Task:
        return Task(config=self.tasks_config["local_transport_task"], output_json=LocalTransportationAnalysis)

    @agent
    def plan_merger_specialist(self) -> Agent:
        return Agent(
            config=self.agents_config["plan_merger_specialist"]
        )

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
    def plan_verification_specialist(self) -> Agent:
        return Agent(
            config=self.agents_config["plan_verification_specialist"],
            tools=[Z3SolverTool()]
        )

    @task
    def area_verification_task(self) -> Task:
        return Task(config=self.tasks_config["plan_verification_task"], output_json=AreaVerificationResult)

    @task
    def city_verification_task(self) -> Task:
        return Task(config=self.tasks_config["plan_verification_task"], output_json=CityVerificationResult)

    @task
    def within_city_verification_task(self) -> Task:
        return Task(config=self.tasks_config["plan_verification_task"], output_json=WithinCityVerificationResult)
        

    # @crew
    # def crew(self, layer: str) -> Crew:
    #     active_agents = []
    #     active_tasks = []

    #     for agent_name, is_active in self.activated_agents.items():
    #         if is_active:
    #             agent_method = getattr(self, agent_name, None)
    #             if callable(agent_method):
    #                 active_agents.append(agent_method())
                
    #             # Handle task names correctly for different agent types
    #             if agent_name == "orchestrator":
    #                 task_methods = [
    #                     self.request_analysis_task,
    #                     self.plan_coordination_task
    #                 ]
    #                 if layer == "area":
    #                     task_methods.append(self.area_results_merge_task)
    #                 elif layer == "city":
    #                     task_methods.append(self.city_results_merge_task)
    #                 elif layer == "within_city":
    #                     task_methods.append(self.within_city_results_merge_task)
    #                 for task_method in task_methods:
    #                     active_tasks.append(task_method())
    #             else:
    #                 task_name = agent_name.replace("_specialist", "") + "_task"
    #                 task_method = getattr(self, task_name, None)
    #                 if callable(task_method):
    #                     # Insert at the second-to-last position in active_tasks
    #                     active_tasks.insert(len(active_tasks) - 1, task_method())
        
    #     return Crew(
    #         agents=active_agents,
    #         tasks=active_tasks,
    #         process=Process.sequential,
    #         verbose=True,
    #         memory=False
    #     )
        
    def crew_plan_next(self) -> Crew:
        return Crew(
            agents=[self.orchestrator()],
            tasks=[self.plan_next_task()],
            process=Process.sequential,
            verbose=True,
            memory=False
        )
    
    def crew_split_task(self, agent_name: str) -> Crew:
        agent_dict = {
            "intercity_transit_specialist": [self.intercity_transit_specialist()],
            "accommodation_search_specialist": [self.accommodation_search_specialist()],
            "activities_planning_specialist": [self.activities_planning_specialist()],
            "restaurant_recommendations_specialist": [self.restaurant_recommendations_specialist()],
            "local_transport_specialist": [self.local_transport_specialist()],
        }
        
        task_dict = {
            "intercity_transit_specialist": [self.intercity_transit_split_task()],
            "accommodation_search_specialist": [self.accommodation_search_split_task()],
            "activities_planning_specialist": [self.activities_planning_split_task()],
            "restaurant_recommendations_specialist": [self.restaurant_recommendations_split_task()],
            "local_transport_specialist": [self.local_transport_split_task()],
        }
        return Crew(
            agents=agent_dict[agent_name],
            tasks=task_dict[agent_name],
            process=Process.sequential,
            verbose=True,
            memory=False
        )
        
    def crew_run_task(self, agent_name: str) -> Crew:
        agent_dict = {
            "area_analysis_specialist": [self.area_analysis_specialist()],
            "city_selection_specialist": [self.city_selection_specialist()],
            "intercity_transit_specialist": [self.intercity_transit_specialist()],
            "accommodation_search_specialist": [self.accommodation_search_specialist()],
            "activities_planning_specialist": [self.activities_planning_specialist()],
            "restaurant_recommendations_specialist": [self.restaurant_recommendations_specialist()],
            "local_transport_specialist": [self.local_transport_specialist()],
        }
        
        task_dict = {
            "area_analysis_specialist": [self.area_analysis_task()],
            "city_selection_specialist": [self.city_selection_task()],
            "intercity_transit_specialist": [self.intercity_transit_task()],
            "accommodation_search_specialist": [self.accommodation_search_task()],
            "activities_planning_specialist": [self.activities_planning_task()],
            "restaurant_recommendations_specialist": [self.restaurant_recommendations_task()],
            "local_transport_specialist": [self.local_transport_task()],
        }
        return Crew(
            agents=agent_dict[agent_name],
            tasks=task_dict[agent_name],
            process=Process.sequential,
            verbose=True,
            memory=False
        )
        
    def crew_verify(self, layer: str) -> Crew:
        task_dict = {
            "area": [self.area_verification_task()],
            "city": [self.city_verification_task()],
            "within_city": [self.within_city_verification_task()],
        }
        return Crew(
            agents=[self.plan_verification_specialist()],
            tasks=task_dict[layer],
            process=Process.sequential,
            verbose=True,
            memory=False
        )