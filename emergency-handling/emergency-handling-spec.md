

- Managed agent team with coordinator and sub agents similar to the pattern in the repo root, but this entire project sholud be inside this emergency-handling folder. the point of the project is to handle emergency scenarios
- Input (for this case we need demo input similar to the synthetic-data folder):
    - Emergency scenario description
    - Living situation (household members, etc.), location and available resources (special items like compass, radio, etc.)
    - Valuable skills and expertise
- Emergency types: Power or water outage, flooding, wildfires, earthquakes, hurricanes, zombie apocalypse
- Output: One nicely styled HTML page summarizing the emergency scenario and what the subagents found out from third party research (in our demo case with demo data of fictive emergency encoded in a research skill)
- Use case agent structure
    - Orchestrator that orchestrates the subagents and sends them to reserach and reason about the emergeny. once they are finished the orchestrator builds the html page and sends it as full output to the client and client stores it in repository
    - 1. subagent: Researcher that gathers information about the emergency scenario from third-party sources and encodes it into a structured format for the orchestrator to use. Researcher needs to complete first, then other subagents can be dispatched
    - 2. subagent: Mental support agent that provides emotiional support to be included in the final HTML page for the client to review.
    - 3. subagent: Logistics and survival expert agent that assesses the available resources and living situation to provide practical advice and recommendations for handling the emergency. (example: we have no water avaialble how do we get drinking water)
    - 4. subagent: medical specialist that provides medical advice and a brief faq for the html document for potential signs of physical issues the household members should watch for.