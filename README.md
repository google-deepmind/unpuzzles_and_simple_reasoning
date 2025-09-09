# unpuzzles_and_simple_reasoning

This project provides the evaluation data for the paper
Alan Malek, Ge, Lazic, Jin, György, Szepesvári. "Frontier LLMs Still Struggle
with Simple Reasoning Tasks," 2025.

It provides three distinct datasets, presented in JSON format:

- The collection of simple reasoning tasks, which have been procedurally
  generated with a specific seed. There are 1120 questions separated into 5
  categories. Each entry has 1240 entries with fields:
    'question' The question
    'answer' The correct answer
    'task' Which task; corresponds to the task names in the paper
    'custom_id" An id unique to each question; useful for batch-mode APIs.
    Various hyperparameter settings.
- The unpuzzles, which consists of 97 pairs of original puzzles and unpuzzled
  versions.
- The context-shifted unpuzzles, which consists of 69 sets of an original
  puzzle (sometimes slightly modified to allow for automatic verification), an
  unpuzzle, and an unpuzzle written in a different context.

In addition, code is provided to extract and grade answers from the model for
the simple reasoning and context-shifte unpuzzle tasks. See
/notebooks/evaluate.ipynb
for a demonstration of how to load and grade all tasks, using the openAI API
as an example.

Otherwise, the datasets can be loaded like any JSON file:
'''
import json
with open(f"/datasets/simple_reasoning.json", "r") as f:
    simple_reasoning_data = json.load(f)
with open(f"/datasets/unpuzzles.json", "r") as f:
    unpuzzle_data = json.load(f)
with open(f"/datasets/shifted_unpuzzles.json", "r") as f:
    shifter_unpuzzle_data = json.load(f)
'''

## Installation

0. (Optional but highly recommended) Setup a virtual environment.
```
sudo apt-get install virtualenv python3-venv
virtualenv myproject  # or python3 -m venv myproject
source myproject/bin/activate
```
To exit a virtual env, use the deactivate command.

1. Make sure the following packages are installed.
```
pip install -r requirements.txt
```

2. Launch a notebook, either via jupyter
```
jupyter notebook
```
then navigate to /notebooks/evaluate.ipynb and follow the instructions.

## Usage

See the companion notebook for usage.

## Citing this work

@misc{malek2025frontierllmsstrugglesimple,
      title={Frontier LLMs Still Struggle with Simple Reasoning Tasks},
      author={Alan Malek and Jiawei Ge and Nevena Lazic and Chi Jin and
              András György and Csaba Szepesvári},
      year={2025},
      eprint={2507.07313},
      archivePrefix={arXiv},
      primaryClass={cs.CL},
      url={https://arxiv.org/abs/2507.07313},
}

## License and disclaimer

Copyright 2025 Google LLC

All software is licensed under the Apache License, Version 2.0 (Apache 2.0);
you may not use this file except in compliance with the Apache 2.0 license.
You may obtain a copy of the Apache 2.0 license at:
https://www.apache.org/licenses/LICENSE-2.0

All other materials are licensed under the Creative Commons Attribution 4.0
International License (CC-BY). You may obtain a copy of the CC-BY license at:
https://creativecommons.org/licenses/by/4.0/legalcode

Unless required by applicable law or agreed to in writing, all software and
materials distributed here under the Apache 2.0 or CC-BY licenses are
distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
either express or implied. See the licenses for the specific language governing
permissions and limitations under those licenses.

This is not an official Google product.
