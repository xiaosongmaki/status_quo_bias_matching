# School-Student Matching Simulation

This project implements a simulation of the Deferred Acceptance (DA) algorithm for school-student matching, with a focus on analyzing strategic behavior.

## Key Components

### MatchingSimulation Class (`matching_simulation.py`)

The core class that implements the matching logic:

- `generate_all_preferences()`: Generates possible preference orderings for students and schools
- `da_algorithm()`: Implements the Deferred Acceptance algorithm for matching
- `generate_updated_preferences()`: Generates possible preference updates for second round matching
- Built-in debugging capabilities for detailed process tracking

Key features:
- Supports 4 students (s1-s4) and 4 schools (c1-c4)
- Implements preference generation with controlled sampling
- Provides detailed matching process visualization in debug mode

### Simulation Runner (`run_matching.py`) 

Orchestrates the simulation process:

- `run_simulation()`: Main function that:
  - Generates preference combinations
  - Runs first round matching with honest/strategic preferences
  - Simulates second round with preference updates
  - Records beneficial strategic cases
- `analyze_results()`: Provides statistical analysis of simulation results
- `save_first_beneficial_case()`: Saves detailed data for first found beneficial strategy
- `save_all_beneficial_cases()`: Saves comprehensive data for all beneficial strategies

## Key Features

1. Two-round matching simulation
2. Strategic behavior analysis
3. Preference sampling and updating
4. Detailed case recording and analysis
5. JSON output for result persistence

## Output Files

The simulation generates several JSON files:
- `beneficial_simulation_results_[timestamp].json`: All simulation results
- `first_beneficial_case.json`: First found beneficial strategic case
- `all_beneficial_cases_[timestamp].json`: All found beneficial strategic cases

## Usage

Run the simulation:
