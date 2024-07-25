# CMPM-146-P4
## Groupmates:
- Aryan Sidbatte
    - Wrote the code for manualHTN.py
    - Wrote optimization for autoHTN.py
- Cyrus Amalan
    - Wrote testcases for autoHTN.py
    - Wrote the code for autoHTN.py


## Overview
This project implements a Hierarchical Task Network (HTN) planner using the Pyhop library. The HTN planner is designed to simulate a crafting process with multiple resources, tools, and goals. The planner decides the optimal sequence of actions to achieve specified goals based on a set of recipes and available resources.

## Files
- manualHTN.py
    - Implements a hard-coded approach to solving a crafting problem using HTN. This file contains specific operators and methods to accomplish goals based on predefined rules.

- autoHTN.py
    - Implements an automated approach to solving a crafting problem using HTN. The script loads rules from a JSON file (crafting.json) and dynamically declares operators and methods based on the loaded data.

- crafting.json
    - Contains the data structure used by autoHTN.py to define the crafting rules, including requirements, consumables, products, and time for each action.

## Heuristics

1. Avoid Redundant Tools: If the planner is in the process of producing a tool and it is already present in the call stack, it avoids creating it again.

    - This helps in avoiding redundant or cyclical creation of tools.

2. Sufficient Resources Check: For production tasks involving items, the heuristic checks if there are already enough resources available to fulfill all subsequent tasks requiring that item.

    - This prevents overproduction of items beyond the immediate need.

3. Priority for Tools: The heuristic optimizes for the creation of advanced tools (e.g., iron_axe) by ensuring lower-level tools (e.g., wooden_axe, stone_axe) aren't unnecessarily created if an advanced tool is already in the pipeline.

    - Ensures the planner doesn't produce lower-tier tools once higher-tier ones are available or being produced.

4. Iron Pickaxe Production: A specific check ensures that if the number of ingots required is between 1 and 11, an iron_pickaxe is prioritized, optimizing ingot usage.

    - This guides the crafting process towards efficient use of iron resources.

5. Wooden Axe Production: The heuristic assesses if the amount of wood required is less than or equal to 9, ensuring the production of a wooden_axe is optimized.

    - This prevents unnecessary crafting when the goal can be met with existing resources.
