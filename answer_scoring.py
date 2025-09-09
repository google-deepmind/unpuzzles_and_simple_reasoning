# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

"""Utilities for scoring answers after extraction.

Each type of task has an associated scoring function called <name>_task.
These function are designed to receive, as input, the output of the
corresponding anster_extraction function.

Tasks are:
  count: For the word and character counting tasks.
  mathgap: For the mathgap tasks, both with diverse rules and irrelevant
    information.
  travel: For the travel plannnig task.
  logic: For both the evaluation and the negation logic task.
"""


from typing import Mapping, Union


def score_travel_eval(
    correct_answer: dict[str, Union[str, float]],
    user_solution: list[tuple[str, str, str]],
) -> bool:
  """Scores a solution to a travel task.

  This method extracts the solution to the travel task from user_solution,
  then checks to see if it satisfies all the constraints defined in
  correct_answer.

  Args:
    correct_answer: The correct answer details containing: -
      "city_start": Start city. - "city_end": End city. - "total_budget":
      Maximum allowed budget. - "steps": Minimum number of unique cities to
      visit. - "graph": The graph of connections. - "costs": Costs of
      transportation.
    user_solution: User"s travel plan in format: [(city1, city2,
      transportation_method), ...]

  Returns:
    Whether the solution satisfies all constraints.
  """
  # Check if the plan ends at city_end
  if not user_solution or user_solution[-1][1] != correct_answer["city_end"]:
    return False
  if not _validate_connectivity(
      city_start=correct_answer["city_start"],
      num_cities=correct_answer["steps"],
      graph=correct_answer["graph"],
      user_solution=user_solution
  ):
    return False
  if not _validate_budget(
      costs=correct_answer["costs"],
      total_budget=correct_answer["total_budget"],
      user_solution=user_solution,
  ):
    return False

  # Print results. To debug, print the errors.
  return True


def _validate_connectivity(
    city_start: str,
    num_cities: int,
    graph: dict[str, dict[str, list[str]]],
    user_solution: list[tuple[str, str, str]],
) -> bool:
  """Checks that the travel plan satisfies connectivity constraints."""
  # Validate each step in the travel plan
  visited_cities = set()  # To track unique cities visited
  current_city = city_start
  for step in user_solution:
    if len(step) != 3:
      return False

    city1, city2, mode = step
    # Validate connectivity
    if (
        city1 not in graph
        or city2 not in graph[city1]
        or mode not in graph[city1][city2]
    ):
      return False

    # Validate continuity
    if city1 != current_city:
      return False
    visited_cities.add(city1)
    current_city = city2
    visited_cities.add(current_city)  # Add the final city to visited cities

  # Check if the minimum number of unique cities is visited
  if len(visited_cities) < num_cities:
    return False

  return True


def _validate_budget(
    costs: dict[str, float],
    total_budget: float,
    user_solution: list[tuple[str, str, str]],
) -> bool:
  """Checks that the travel plan satisfies the budget constraint."""
  total_cost = 0
  for step in user_solution:
    city1, city2, mode = step
    try:
      if city1 + city2 + mode in costs:
        total_cost += costs[city1 + city2 + mode]
      else:
        return False
    except TypeError:
      return False

  # Check if budget is exceeded
  if total_cost > total_budget:
    return False
  return True


def score_count_eval(correct_answer: Mapping[str, int], answer: list[int]):
  if not answer:
    return False
  bools = (a1 == a2 for (a1, a2) in zip(answer, correct_answer.values()))
  return all(bools)


def score_mathgap_eval(correct_answer: str, answer: str):
  return correct_answer == answer


def score_logic_eval(correct_answer: str, answer: str) -> bool:
  if not answer:
    return False
  return correct_answer.lower() == answer.lower()


def score_unpuzzle_eval(s1: str, s2: str):
  return s1.lower().strip(" ") == s2.lower().strip(" ")


def score_eval(json_entry, answer) -> bool:
  """Scores an extracted answer from an LLM response."""
  if json_entry["task"] in ["character_count", "word_count"]:
    return score_count_eval(json_entry["answer"], answer)
  elif json_entry["task"] in ["mathgap_diverse", "mathgap_irrelevant"]:
    return score_mathgap_eval(json_entry["answer"], answer)
  elif json_entry["task"] == "travel":
    return score_travel_eval(json_entry["answer"], answer)
  elif json_entry["task"] in ["logic_negation", "logic_evaluation"]:
    return score_logic_eval(json_entry["answer"], answer)
  else:
    return False
