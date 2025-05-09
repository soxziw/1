from typing import Dict, Any, List
from crewai import Agent, Crew, Task, Process
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool, ScrapeWebsiteTool
import yaml
import os

from maia.tools.travel_api_tool import (
    FlightSearchTool, 
    AccommodationSearchTool, 
    PointsOfInterestSearchTool
)
from maia.tools.constraint_validation_tool import ConstraintValidationTool

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
            "dining_recommendations_specialist": False,
            "local_transport_specialist": False,
            "constraint_verification_specialist": False
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
            self.activated_agents["dining_recommendations_specialist"] = True
            self.activated_agents["local_transport_specialist"] = True
        elif layer_name == "verification":
            self.activated_agents["constraint_verification_specialist"] = True

@CrewBase
class MAIA(MAIABase):
    def process_request(self, complete_input: Dict[str, Any]) -> Dict[str, Any]:
        result = self.crew().kickoff(inputs=complete_input)
        return result

    @agent
    def orchestrator(self) -> Agent:
        return Agent(
            config=self.agents_config["orchestrator"],
            tools=[ConstraintValidationTool(), SerperDevTool()]
        )

    @task
    def request_analysis_task(self) -> Task:
        return Task(config=self.tasks_config["request_analysis_task"])

    @task
    def plan_coordination_task(self) -> Task:
        return Task(config=self.tasks_config["plan_coordination_task"])

    @task
    def final_plan_compilation_task(self) -> Task:
        return Task(config=self.tasks_config["final_plan_compilation_task"])

    @agent
    def area_analysis_specialist(self) -> Agent:
        return Agent(
            config=self.agents_config["area_analysis_specialist"],
            tools=[SerperDevTool(), ScrapeWebsiteTool()]
        )

    @task
    def area_analysis_task(self) -> Task:
        return Task(config=self.tasks_config["area_analysis_task"])

    @agent
    def city_selection_specialist(self) -> Agent:
        return Agent(
            config=self.agents_config["city_selection_specialist"],
            tools=[SerperDevTool(), ScrapeWebsiteTool()]
        )

    @task
    def city_selection_task(self) -> Task:
        return Task(config=self.tasks_config["city_selection_task"])

    @agent
    def intercity_transit_specialist(self) -> Agent:
        return Agent(
            config=self.agents_config["intercity_transit_specialist"],
            tools=[SerperDevTool(), ScrapeWebsiteTool(), FlightSearchTool()]
        )

    @task
    def intercity_transit_task(self) -> Task:
        return Task(config=self.tasks_config["intercity_transit_task"])

    @agent
    def accommodation_search_specialist(self) -> Agent:
        return Agent(
            config=self.agents_config["accommodation_search_specialist"],
            tools=[SerperDevTool(), ScrapeWebsiteTool(), AccommodationSearchTool()]
        )

    @task
    def accommodation_search_task(self) -> Task:
        return Task(config=self.tasks_config["accommodation_search_task"])

    @agent
    def activities_planning_specialist(self) -> Agent:
        return Agent(
            config=self.agents_config["activities_planning_specialist"],
            tools=[SerperDevTool(), ScrapeWebsiteTool(), PointsOfInterestSearchTool()]
        )

    @task
    def activities_planning_task(self) -> Task:
        return Task(config=self.tasks_config["activities_planning_task"])

    @agent
    def dining_recommendations_specialist(self) -> Agent:
        return Agent(
            config=self.agents_config["dining_recommendations_specialist"],
            tools=[SerperDevTool(), ScrapeWebsiteTool(), PointsOfInterestSearchTool()]
        )

    @task
    def dining_recommendations_task(self) -> Task:
        return Task(config=self.tasks_config["dining_recommendations_task"])

    @agent
    def local_transport_specialist(self) -> Agent:
        return Agent(
            config=self.agents_config["local_transport_specialist"],
            tools=[SerperDevTool(), ScrapeWebsiteTool()]
        )

    @task
    def local_transport_task(self) -> Task:
        return Task(config=self.tasks_config["local_transport_task"])

    @agent
    def constraint_verification_specialist(self) -> Agent:
        return Agent(
            config=self.agents_config["constraint_verification_specialist"],
            tools=[ConstraintValidationTool()]
        )

    @task
    def constraint_verification_task(self) -> Task:
        return Task(config=self.tasks_config["constraint_verification_task"])

    @crew
    def crew(self) -> Crew:
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
                        self.plan_coordination_task,
                        self.final_plan_compilation_task
                    ]
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