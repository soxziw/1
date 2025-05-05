# MAIA: Multi-Agent Itinerary Assistant

MAIA is an advanced travel planning system leveraging Large Language Models (LLMs) within a multi-agent framework. The system employs a hierarchical multi-agent architecture where specialized agents handle distinct aspects of travel planning (high-level area selection, inter-city travel, intra-city activities).

## Key Features

- **Hierarchical Agent Architecture**: Organizes travel planning into specialized layers
  - Area layer for destination analysis and date selection
  - City layer for city selection and inter-city transit planning
  - Within-city layer for accommodations, activities, dining, and local transport
  - Verification layer to ensure constraint adherence

- **Strict Constraint Verification**: Rigorously validates that plans adhere to user constraints
  - Time constraints (dates, durations, timing)
  - Budget constraints (total cost, category allocations)
  - Preference constraints (accommodations, activities, dining)

- **Real-Time API Integration**: Connects with travel APIs for accurate information
  - Flights and transportation
  - Accommodations
  - Points of interest and activities

- **User-Friendly Interface**: Designed for easy interaction and clear results
  - Natural language input processing
  - Structured, formatted travel plans
  - Markdown output for easy reading and sharing

## Installation

Ensure you have Python >=3.10 <3.13 installed.

1. Clone this repository
   ```bash
   git clone https://github.com/yourusername/maia.git
   cd maia
   ```

2. Install dependencies
   ```bash
   pip install -e .
   ```

3. Create a `.env` file with your API keys:
   ```
   OPENAI_API_KEY=your_openai_api_key
   SERPAPI_API_KEY=your_serpapi_api_key
   SERPER_API_KEY=your_serper_api_key
   ```

## Usage

### Interactive Mode

Run MAIA interactively:

```bash
python -m maia.main
```

Follow the prompts to enter your travel request and preferences.

### Command-Line Mode

Process a travel request directly from the command line:

```bash
python -m maia.main --request "I want to plan a trip to Japan for 10 days in October 2023 with a budget of $5000." --output "japan_trip.md"
```

### As a Module

Import and use MAIA in your own Python code:

```python
from maia.main import process_request

travel_request = "I want to plan a trip to Europe, visiting Paris and Rome for 2 weeks in summer 2023 with a budget of $8000."
result = process_request(travel_request)
```

## Example

See the `examples` directory for sample code:

```bash
python examples/example_request.py
```

## System Architecture

MAIA uses a hierarchical multi-agent system powered by the CrewAI framework:

1. **Orchestrator Layer**: Analyzes user requests, extracts constraints, and coordinates specialized agents
2. **Area Layer**: Analyzes destination regions, seasonality, and optimal travel dates
3. **City Layer**: Selects specific cities, allocates time, and plans inter-city transportation
4. **Within-City Layer**: Plans accommodations, activities, dining, and local transportation
5. **Verification Layer**: Ensures all aspects of the plan adhere to user constraints

Each layer contains specialized agents with specific roles and capabilities:

- **Destination & Timeline Specialist**: Analyzes high-level constraints
- **City Selection & Duration Specialist**: Optimizes city selection and durations
- **Intercity Transportation Specialist**: Plans travel between cities
- **Accommodation Specialist**: Finds suitable lodging options
- **Sites & Activities Specialist**: Curates engaging activities
- **Dining & Culinary Specialist**: Recommends dining experiences
- **Local Transportation Specialist**: Plans efficient local transport
- **Constraint Verification Specialist**: Validates plan adherence to constraints

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.