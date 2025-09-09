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

"""Utilities for extracting answers from LLM responses.

Each type of task has an associated extraction function called <name>_task.
The output of these functions is formatted to be passed into the corresponding
scoring function.

Evals types are:
  count: For the word and character counting tasks.
  mathgap: For the mathgap tasks, both with diverse rules and irrelevant
    information.
  travel: For the travel plannnig task.
  logic: For both the evaluation and the negation logic task.
"""

import ast
import re

from typing import Any


def _text_to_int(s: str) -> int:
  """Converts a string name to an integer, e.g. 'five'->5."""
  text_to_int_dict = {
      "zero": 0,
      "one": 1,
      "two": 2,
      "three": 3,
      "four": 4,
      "five": 5,
      "six": 6,
      "seven": 7,
      "eight": 8,
      "nine": 9,
      "ten": 10,
      "eleven": 11,
      "twelve": 12,
      "thirteen": 13,
      "fourteen": 14,
      "fifteen": 15,
      "sixteen": 16,
      "seventeen": 17,
      "eighteen": 18,
      "nineteen": 19,
      "twenty": 20,
  }
  return text_to_int_dict[s] if s in text_to_int_dict else None


def _insert_quotes_in_tuples(candidate: str) -> str:
  """Converts unquoted tokens inside parentheses into quoted strings.

  E.g. (Fresno, Irvine, motorhome) -> ('Fresno', 'Irvine', 'motorhome')
        (Fort Wayne, Boise, flight) -> ('Fort Wayne', "Boise', 'flight')

  Args:
    candidate: The string to modify.

  Returns:
    The modified string.
  """

  # This finds text inside a single pair of parentheses (...)
  # such as "Fresno, Irvine, motorhome"
  def replacer(match):
    content = match.group(1)  # text inside the parentheses
    parts = (p.strip() for p in content.split(","))

    quoted_parts = []
    for p in parts:
      # If the user already typed something like 'Santa Ana', keep it
      if (p.startswith("'") and p.endswith("'")) or (
          p.startswith('"') and p.endswith('"')
      ):
        quoted_parts.append(p)
      else:
        quoted_parts.append(f"'{p}'")

    return f"({', '.join(quoted_parts)})"

  # Replace each parenthesized group in the candidate string with its quoted
  # version. This only replaces parentheses that do NOT themselves contain
  # parentheses.
  return re.sub(r"\(([^()]+)\)", replacer, candidate)


def extract_travel_eval(response: str) -> list[tuple[str, str, str]]:
  """Extracts the travel plan from the user's response.

  Handles both Python code block and plain text cases.

  Args:
    response: The user's response, which may contain a travel plan in
      Python list format either within a code block or directly as text.

  Returns:
    A clean list of tuples representing the travel plan, e.g.,
      [('Austin', 'Anchorage', 'car'),
      ('Anchorage', 'Indianapolis', 'hyperloop'), ...].
      If an error occurs, returns an empty list.
  """

  # Try to match a Python code block first
  code_block_re = re.compile(r"```python\n(.*?)```", re.DOTALL)
  matches = code_block_re.findall(response)

  if not matches:
    return []
  # If a code block is found, try to evaluate it
  travel_plan_str = matches[-1].strip()

  # Ensure the string is formatted as a valid Python list of tuples
  travel_plan_str = _insert_quotes_in_tuples(travel_plan_str)

  try:
    # Attempt to evaluate the Python code block as a list of tuples
    travel_plan = ast.literal_eval(travel_plan_str)
    travel_plan = (
        list(travel_plan)
        if isinstance(travel_plan[0], tuple)
        else [travel_plan]
    )

    # If the result is a list of tuples, check its format
    if isinstance(travel_plan, list) and all(
        isinstance(item, tuple) and len(item) == 3 for item in travel_plan
    ):
      return travel_plan
    else:
      return []
  except SyntaxError:
    return []


def _remove_text_formatting(response: str) -> str:
  # Remove any # marks or ** marks or \\ marks around the number
  response = re.sub(r"#(\d+)", r"\1", response)
  response = re.sub(r"(\d+)#", r"\1", response)
  response = re.sub(r"\*\*(\d+)", r"\1", response)
  response = re.sub(r"(\d+)\*\*", r"\1", response)
  response = re.sub(r"\\(\d+)", r"\1", response)
  response = re.sub(r"(\d+)\\", r"\1", response)
  return response


def extract_count_eval(response: str, k: int) -> list[int]:
  """Extracts the answer from a properly formatted response.

  Handles both word and character counting modes.
  Will not successfully extract an answer and return an empty list if k is not
  correctly specified.

  Args:
    response: The response to extract the answer from.
    k: The number of answers to extract.

  Returns:
    A list of answers extracted from the response.
  """
  count_re = re.compile(r"appear.*?(\d+).*?time")
  count_multi_re = re.compile(r".*appear \**\\?\[(.+)?\\?\]\** time")

  if k == 1:
    # Single word or character case
    match_obj = count_re.search(response)
    ans = ""
    if not match_obj:
      return [ans]
    s = match_obj.group(1)
    s = _remove_text_formatting(s)
    try:
      ans = int(s)
    except ValueError:
      ans = _text_to_int(s)
    return [ans]
  else:
    # Multiple word case (word counting mode)
    match_obj = count_multi_re.search(response)
    if not match_obj:
      return [ans] * k
    else:
      ans_list = match_obj.group(1).split(",")
      answers = []
      for ans in ans_list:
        try:
          ans = _remove_text_formatting(ans)
          ans = int(ans)
        except ValueError:
          ans = _text_to_int(ans)
        answers.append(ans)
      if len(answers) != k:
        return [""]
      return answers


def extract_mathgap_eval(response: str) -> str:
  """Extracts the answer from a response to a mathgap task.

  Args:
    response: The response to extract the answer from.
  Returns:
    str: The answer extracted from the response.
  """
  matches = re.findall(r"boxed{([^}]*)}", response)
  answer = None

  if not matches:
    return answer
  try:
    answer = int(matches[-1])
  except ValueError:
    answer = None
  return answer

extract_answer_html = re.compile(r".*<answer>([A-D])</answer>")
extract_answer_boxed = re.compile(r"boxed\{([A-D])\}")
extract_answer_sentence = re.compile(r"answer:? ([A-D])")
extract_answer_sentence2 = re.compile(r"answer is:? ([A-D])")
extract_answer_sentence2 = re.compile(r"answer.*?([A-D])")
compiled_res = [extract_answer_html,
                extract_answer_boxed,
                extract_answer_sentence,
                extract_answer_sentence2]


def extract_logic_eval(response: str) -> str:
  """Extracts a multiple choice answer, as needed by the logic tasks."""
  for comp in compiled_res:
    match_object = comp.search(response)
    if match_object:
      return match_object.group(1)
  return ""

find_answers = [
    re.compile(r"boxed\{(.+?)\}"),
    re.compile(r"Answer.*\*{2}(.+)\*{2}"),
    re.compile(r"\*{2}Answer:? (.+)\*{2}"),
    re.compile(r"answer is:? (.+)."),
    re.compile(r"\*{2}answer is:? (.+)\*{2}"),
    re.compile(r"Answer: (.+)."),
    re.compile(r"/$(.+?)/$"),
]


def extract_unpuzzle_eval(response: str) -> str:
  for regex in find_answers:
    matches = regex.findall(response)
    if matches:
      for s in matches:
        if s not in ["your answer", "answer"]:
          return s
  return ""


def extract_eval(json_entry: dict[str, Any], response: str) -> str:
  """Extracts the answer from a response to a task."""
  if json_entry["task"] in ["character_count", "word_count"]:
    return extract_count_eval(response, k=json_entry["k"])
  elif json_entry["task"] in ["mathgap_diverse", "mathgap_irrelevant"]:
    return extract_mathgap_eval(response)
  elif json_entry["task"] == "travel":
    return extract_travel_eval(response)
  elif json_entry["task"] in ["logic_negation", "logic_evaluation"]:
    return extract_logic_eval(response)
  else:
    return ""
