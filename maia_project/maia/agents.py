from typing import Dict, Any, List
from crewai import Agent, Crew, Task, Process
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
            "area_specialist": False,
            "city_selection_specialist": False,
            "intercity_transit_specialist": False,
            "accommodation_specialist": False,
            "activities_specialist": False,
            "dining_specialist": False,
            "local_transport_specialist": False,
            "verification_specialist": False
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
    def process_request(self, complete_input: Dict[str, Any]) -> Dict[str, Any]:
        result = self.crew().kickoff(inputs=complete_input)
        return result

    def orchestrator(self):
        return Agent(
            config=self.agents_config["orchestrator"],
            tools=[ConstraintValidationTool(), SerperDevTool()]
        )

    def request_analysis_task(self):
        return Task(config=self.tasks_config["request_analysis_task"])

    def plan_coordination_task(self):
        return Task(config=self.tasks_config["plan_coordination_task"])

    def final_plan_compilation_task(self):
        return Task(config=self.tasks_config["final_plan_compilation_task"])

    def area_specialist(self):
        return Agent(
            config=self.agents_config["area_specialist"],
            tools=[SerperDevTool(), ScrapeWebsiteTool()]
        )

    def area_analysis_task(self):
        return Task(config=self.tasks_config["area_analysis_task"])

    def city_selection_specialist(self):
        return Agent(
            config=self.agents_config["city_selection_specialist"],
            tools=[SerperDevTool(), ScrapeWebsiteTool()]
        )

    def intercity_transit_specialist(self):
        return Agent(
            config=self.agents_config["intercity_transit_specialist"],
            tools=[SerperDevTool(), ScrapeWebsiteTool(), FlightSearchTool()]
        )

    def city_selection_task(self):
        return Task(config=self.tasks_config["city_selection_task"])

    def intercity_transit_task(self):
        return Task(config=self.tasks_config["intercity_transit_task"])

    def accommodation_specialist(self):
        return Agent(
            config=self.agents_config["accommodation_specialist"],
            tools=[SerperDevTool(), ScrapeWebsiteTool(), AccommodationSearchTool()]
        )

    def activities_specialist(self):
        return Agent(
            config=self.agents_config["activities_specialist"],
            tools=[SerperDevTool(), ScrapeWebsiteTool(), PointsOfInterestSearchTool()]
        )

    def dining_specialist(self):
        return Agent(
            config=self.agents_config["dining_specialist"],
            tools=[SerperDevTool(), ScrapeWebsiteTool(), PointsOfInterestSearchTool()]
        )

    def local_transport_specialist(self):
        return Agent(
            config=self.agents_config["local_transport_specialist"],
            tools=[SerperDevTool(), ScrapeWebsiteTool()]
        )

    def accommodation_search_task(self):
        return Task(config=self.tasks_config["accommodation_search_task"])

    def activities_planning_task(self):
        return Task(config=self.tasks_config["activities_planning_task"])

    def dining_recommendations_task(self):
        return Task(config=self.tasks_config["dining_recommendations_task"])

    def local_transport_task(self):
        return Task(config=self.tasks_config["local_transport_task"])

    def verification_specialist(self):
        return Agent(
            config=self.agents_config["verification_specialist"],
            tools=[ConstraintValidationTool()]
        )

    def constraint_verification_task(self):
        return Task(config=self.tasks_config["constraint_verification_task"])

    def crew(self):
        active_agents = []
        active_tasks = []

        for agent_name, is_active in self.activated_agents.items():
            if is_active:
                agent_method = getattr(self, agent_name, None)
                task_name = agent_name.replace("_specialist", "") + "_task"
                task_method = getattr(self, task_name, None)
                if callable(agent_method):
                    active_agents.append(agent_method())
                if callable(task_method):
                    active_tasks.append(task_method())

        return Crew(
            agents=active_agents,
            tasks=active_tasks,
            process=Process.sequential,
            verbose=True,
            memory=False
        )
