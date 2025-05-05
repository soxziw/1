"""
Hierarchical agent structure for MAIA.
"""

from typing import Dict, Any, List, Optional, Type
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool, ScrapeWebsiteTool
from crewai.agents import CrewAgentConfig
from crewai.tasks import CrewTaskConfig
import json
import os
import yaml

from maia.tools.travel_api_tool import (
    FlightSearchTool, 
    AccommodationSearchTool, 
    PointsOfInterestSearchTool
)
from maia.tools.constraint_validation_tool import ConstraintValidationTool


class MAIABase(CrewBase):
    """
    Base class for MAIA's hierarchical agent structure.
    
    This class provides common functionality for all MAIA agents,
    including configuration loading and constraint management.
    """
    
    def __init__(self):
        """Initialize the MAIA base class."""
        # Load agent and task configurations from YAML files
        self.agents_config = self._load_config("agents.yaml")
        self.tasks_config = self._load_config("tasks.yaml")
        
        # Dictionary to store constraint information
        self.constraints = {}
        
        # Dictionary to store activation status of agents
        self.activated_agents = {
            "orchestrator": True,  # Orchestrator is always active
            "area_specialist": False,
            "city_selection_specialist": False,
            "intercity_transit_specialist": False,
            "accommodation_specialist": False,
            "activities_specialist": False,
            "dining_specialist": False,
            "local_transport_specialist": False,
            "verification_specialist": False
        }
        
        # Call parent initializer
        super().__init__()
    
    def _load_config(self, filename: str) -> Dict[str, Any]:
        """
        Load configuration from a YAML file.
        
        Args:
            filename: Name of the YAML file to load
            
        Returns:
            Dictionary containing the configuration
        """
        config_path = os.path.join(
            os.path.dirname(__file__), "config", filename
        )
        with open(config_path, "r") as f:
            return yaml.safe_load(f)
    
    def update_constraints(self, new_constraints: Dict[str, Any]) -> None:
        """
        Update the constraints dictionary with new constraints.
        
        Args:
            new_constraints: Dictionary of new constraints to add/update
        """
        self.constraints.update(new_constraints)
    
    def activate_agent(self, agent_name: str) -> None:
        """
        Activate a specific agent.
        
        Args:
            agent_name: Name of the agent to activate
        """
        if agent_name in self.activated_agents:
            self.activated_agents[agent_name] = True
    
    def activate_layer(self, layer_name: str) -> None:
        """
        Activate all agents in a specific layer.
        
        Args:
            layer_name: Name of the layer to activate
                (area, city, within_city, verification)
        """
        if layer_name == "area":
            self.activated_agents["area_specialist"] = True
        elif layer_name == "city":
            self.activated_agents["city_selection_specialist"] = True
            self.activated_agents["intercity_transit_specialist"] = True
        elif layer_name == "within_city":
            self.activated_agents["accommodation_specialist"] = True
            self.activated_agents["activities_specialist"] = True
            self.activated_agents["dining_specialist"] = True
            self.activated_agents["local_transport_specialist"] = True
        elif layer_name == "verification":
            self.activated_agents["verification_specialist"] = True


class MAIA(MAIABase):
    """
    MAIA: Multi-Agent Itinerary Assistant.
    
    This class implements the hierarchical agent structure for MAIA,
    providing methods to create and coordinate specialized agents
    for travel planning.
    """
    
    def process_user_request(self, user_request: str) -> Dict[str, Any]:
        """
        Process a user request and generate a travel plan.
        
        Args:
            user_request: The user's travel request as a string
            
        Returns:
            Dictionary containing the travel plan
        """
        # Initialize with the user request
        inputs = {
            "user_request": user_request
        }
        
        # Run the crew
        result = self.crew().kickoff(inputs=inputs)
        
        # Return the result
        return result
    
    # ==================== ORCHESTRATOR LAYER ====================
    
    @agent
    def orchestrator(self) -> Agent:
        """Creates the orchestrator agent that manages the planning process."""
        return Agent(
            config=self.agents_config["orchestrator"],
            tools=[
                ConstraintValidationTool(),
                SerperDevTool()
            ]
        )
    
    @task
    def request_analysis_task(self) -> Task:
        """Task for analyzing the user's request and extracting constraints."""
        return Task(
            config=self.tasks_config["request_analysis_task"]
        )
    
    @task
    def plan_coordination_task(self) -> Task:
        """Task for coordinating the planning process across agents."""
        return Task(
            config=self.tasks_config["plan_coordination_task"]
        )
    
    @task
    def final_plan_compilation_task(self) -> Task:
        """Task for compiling the final travel plan."""
        return Task(
            config=self.tasks_config["final_plan_compilation_task"]
        )
    
    # ==================== AREA LAYER ====================
    
    @agent
    def area_specialist(self) -> Agent:
        """Creates the area specialist agent."""
        return Agent(
            config=self.agents_config["area_specialist"],
            tools=[
                SerperDevTool(),
                ScrapeWebsiteTool()
            ]
        )
    
    @task
    def area_analysis_task(self) -> Task:
        """Task for analyzing the destination area."""
        return Task(
            config=self.tasks_config["area_analysis_task"]
        )
    
    # ==================== CITY LAYER ====================
    
    @agent
    def city_selection_specialist(self) -> Agent:
        """Creates the city selection specialist agent."""
        return Agent(
            config=self.agents_config["city_selection_specialist"],
            tools=[
                SerperDevTool(),
                ScrapeWebsiteTool()
            ]
        )
    
    @agent
    def intercity_transit_specialist(self) -> Agent:
        """Creates the intercity transit specialist agent."""
        return Agent(
            config=self.agents_config["intercity_transit_specialist"],
            tools=[
                SerperDevTool(),
                ScrapeWebsiteTool(),
                FlightSearchTool()
            ]
        )
    
    @task
    def city_selection_task(self) -> Task:
        """Task for selecting cities to include in the itinerary."""
        return Task(
            config=self.tasks_config["city_selection_task"]
        )
    
    @task
    def intercity_transit_task(self) -> Task:
        """Task for planning transportation between cities."""
        return Task(
            config=self.tasks_config["intercity_transit_task"]
        )
    
    # ==================== WITHIN-CITY LAYER ====================
    
    @agent
    def accommodation_specialist(self) -> Agent:
        """Creates the accommodation specialist agent."""
        return Agent(
            config=self.agents_config["accommodation_specialist"],
            tools=[
                SerperDevTool(),
                ScrapeWebsiteTool(),
                AccommodationSearchTool()
            ]
        )
    
    @agent
    def activities_specialist(self) -> Agent:
        """Creates the activities specialist agent."""
        return Agent(
            config=self.agents_config["activities_specialist"],
            tools=[
                SerperDevTool(),
                ScrapeWebsiteTool(),
                PointsOfInterestSearchTool()
            ]
        )
    
    @agent
    def dining_specialist(self) -> Agent:
        """Creates the dining specialist agent."""
        return Agent(
            config=self.agents_config["dining_specialist"],
            tools=[
                SerperDevTool(),
                ScrapeWebsiteTool(),
                PointsOfInterestSearchTool()
            ]
        )
    
    @agent
    def local_transport_specialist(self) -> Agent:
        """Creates the local transport specialist agent."""
        return Agent(
            config=self.agents_config["local_transport_specialist"],
            tools=[
                SerperDevTool(),
                ScrapeWebsiteTool()
            ]
        )
    
    @task
    def accommodation_search_task(self) -> Task:
        """Task for finding suitable accommodations."""
        return Task(
            config=self.tasks_config["accommodation_search_task"]
        )
    
    @task
    def activities_planning_task(self) -> Task:
        """Task for planning activities and attractions."""
        return Task(
            config=self.tasks_config["activities_planning_task"]
        )
    
    @task
    def dining_recommendations_task(self) -> Task:
        """Task for recommending dining options."""
        return Task(
            config=self.tasks_config["dining_recommendations_task"]
        )
    
    @task
    def local_transport_task(self) -> Task:
        """Task for planning local transportation."""
        return Task(
            config=self.tasks_config["local_transport_task"]
        )
    
    # ==================== VERIFICATION LAYER ====================
    
    @agent
    def verification_specialist(self) -> Agent:
        """Creates the verification specialist agent."""
        return Agent(
            config=self.agents_config["verification_specialist"],
            tools=[
                ConstraintValidationTool()
            ]
        )
    
    @task
    def constraint_verification_task(self) -> Task:
        """Task for verifying constraint adherence."""
        return Task(
            config=self.tasks_config["constraint_verification_task"]
        )
    
    # ==================== CREW CREATION ====================
    
    @crew
    def crew(self) -> Crew:
        """Creates the MAIA crew with activated agents and tasks."""
        # Filter agents based on activation status
        active_agents = []
        for agent_name, is_active in self.activated_agents.items():
            if is_active:
                agent_method = getattr(self, agent_name, None)
                if agent_method and callable(agent_method):
                    active_agents.append(agent_method())
        
        # If no agents are explicitly activated, include all agents
        if len(active_agents) <= 1:  # Only orchestrator is active
            active_agents = self.agents
        
        return Crew(
            agents=active_agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
            memory=False  # Disable memory to avoid ChromaDB dependency
        )