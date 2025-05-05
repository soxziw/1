# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands
- Run project: `crewai run`
- Run tests: `crewai test <iterations> <openai_model_name>`
- Run training: `crewai train <iterations> <filename>`
- Replay execution: `crewai replay <task_id>`
- Install dependencies: `uv install`

## Code Style Guidelines
- Follow PEP 8 for Python code
- Use type annotations with Pydantic for data validation
- Classes: PascalCase (e.g., `TripPlanner`, `FlightSearchTool`)
- Methods/Functions: snake_case (e.g., `run`, `process_results`)
- Variables: snake_case (e.g., `destination_location`)
- Use docstrings for classes and methods
- Handle exceptions with try/except blocks with informative error messages
- Use CrewAI decorators (@agent, @task, @crew) for crew components
- Configuration-driven approach with YAML files

## Project Structure
- Multi-agent AI system using CrewAI framework
- YAML configuration in src/trip_planner/config/
- Custom tools in src/trip_planner/tools/
- Outputs saved to markdown files in root directory


based on current architecture and tools, build up a Multi-Agent Itinerary Assistant to interact with user get their request for planning and generate the  plan implementing the proposal below

MAIA: Multi-Agent Itinerary Assistant, A Constraint-Aware Travel Planning System using LLMs
Abstract: This project proposes the development of MAIA (Multi-Agent Itinerary Assistant), an advanced travel planning system leveraging Large Language Models (LLMs) within a multi-agent framework. Current travel planning tools often struggle with complex user constraints, dynamic data integration, and nuanced personalization. MAIA aims to address these limitations by employing a hierarchical multi-agent architecture where specialized agents handle distinct aspects of travel planning (high-level area selection, inter-city travel, intra-city activities). Agents will interact with real-time APIs (accommodation, points of interest) and incorporate strict constraint verification at each planning layer. The goal is to generate feasible, personalized, and constraint-adherent travel itineraries that surpass the capabilities of existing automated planners.
1. Related Work and Motivation
Planning travel involves juggling numerous variables: destinations, dates, budgets, transportation, accommodation, activities, and personal preferences. 
Specifically, Wonderplan and Mindtrip often focus on itinerary generation but may lack real-time integration or deep constraint handling; TripBuilder integrates with TripAdvisor data but might be less flexible with external data sources or complex, multi-faceted constraints; GuideGeek and Swifty represent conversational AI approaches, often using LLMs, but may not employ a sophisticated multi-agent structure for complex planning and verification.
These existing solutions often face challenges in handling intricate, layered constraints, managing dependencies between planning stages (arrival time dictating first-day activities), and robustly integrating dynamic data from multiple sources simultaneously, lack deep integration with real-time availability/pricing, or fail to rigorously enforce complex user constraints ("must depart after 8 AM," "avoid peak season crowds," "only hotels with >4.0 rating").
MAIA differentiates itself through its explicit multi-agent design focused on hierarchical planning and rigorous constraint verification. This project aims to build MAIA, demonstrating how an LLM-powered multi-agent system can effectively:
Decompose complex travel requests into sub-tasks.
Assign tasks to specialized agents.
Integrate real-time data from diverse APIs.
Strictly adhere to user-defined constraints through dedicated verification steps.
Generate comprehensive and personalized travel itineraries.
2. Proposed Approach & Methodology
MAIA will be a multi-agent system (MAS) potentially orchestrated using a framework of AutoGen and custom-built logic. We will utilize GPT-4o for agent reasoning, planning, natural language understanding, and generation.
An orchestrator agent will parse the user's initial request and delegate tasks to specialized agents. Based on the requirement, only some agents will be activated.
Area layer agent handles broadest constraints: Destination region/country, overall time frame (Month, specific dates), time slot preferences, awareness of peak/off-peak seasons.
City layer “City Selection & Duration Arrangement” selects specific cities based on Area constraints and user preferences, and determines the number of days per city. “Intercity Transit” Agent, plans travel between cities (searches Flights for connections, suggests driving routes via Google Maps).
Within-city layer “Sites/Activities” agent identifies points of interest, tours, activities based on preferences and constraints (opening hours, duration). Uses APIs like TripAdvisor, Google Maps. “Dining” agent recommends restaurants based on cuisine type, budget, location, ratings. Uses APIs like Yelp, Google Maps, TripAdvisor. “Accommodation” agent finds hotels/rentals matching criteria (budget, location, amenities, ratings). Uses APIs like Booking.com, Airbnb. “Local Transport” agent plans intra-city travel (walking routes, public transport via Google Maps, car rental options).
Verification Agent(s) operates at each layer or key decision point to explicitly check if the generated plan segment strictly adheres to the user's constraints (time, budget, preferences, feasibility). Flags violations for replanning. Constraints will be explicitly represented and passed between agents. Verification agents will use LLM reasoning and direct checks (comparing flight times against user constraints) to ensure compliance. Might use PDDL/SMT for verification.
3. Data Sources and API Integration
Accommodation & Dining: Booking.com, Airbnb, Yelp
Points of Interest & Reviews: TripAdvisor, Google Maps
Transportation: Flights, Google Maps (Directions API)
Base Knowledge/Reasoning: Core LLM capabilities (GPT/equivalent)
4. Evaluation Plan
To evaluate the effectiveness of the system, we first measure the percentage of generated itineraries that strictly adhere to all predefined hard constraints, such as budget limits, travel date ranges, and non-negotiable user preferences. Beyond basic compliance, we assess whether the generated plans are logically coherent and practically executable—taking into account factors like realistic travel times between locations and the scheduling of activities during actual opening hours. We further compare the itineraries generated by MAIA with those created manually or by existing planning tools, using qualitative evaluation methods such as user surveys and expert reviews to examine their relevance, degree of personalization, and overall completeness. Finally, we test the system’s robustness by observing how it responds to edge cases, including conflicting constraints, API failures, and scenarios involving limited availability of travel resources.

