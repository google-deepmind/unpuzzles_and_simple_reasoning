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

from absl.testing import absltest

import answer_extraction


class AnswerExtractionTest(absltest.TestCase):

  def test_insert_quotes_in_tuples(self):
    self.assertEqual(
        answer_extraction._insert_quotes_in_tuples(
            "(Fresno, Irvine, motorhome)"
        ),
        "('Fresno', 'Irvine', 'motorhome')",
    )
    self.assertEqual(
        answer_extraction._insert_quotes_in_tuples(
            "(Fort Wayne, Boise, flight)"
        ),
        "('Fort Wayne', 'Boise', 'flight')",
    )

  def test_make_serializable(self):
    self.assertEqual(
        answer_extraction._make_serializable({
            ("Fresno", "Irvine", "motorhome"): 10,
            ("Fort Wayne", "Boise", "flight"): 20,
        }),
        {
            "FresnoIrvinemotorhome": 10,
            "Fort WayneBoiseflight": 20,
        },
    )

  def _text_to_int(self):
    self.assertEqual(answer_extraction._text_to_int("zero"), 0)
    self.assertEqual(answer_extraction._text_to_int("one"), 1)
    self.assertEqual(answer_extraction._text_to_int("two"), 2)
    self.assertEqual(answer_extraction._text_to_int("three"), 3)
    self.assertEqual(answer_extraction._text_to_int("four"), 4)
    self.assertEqual(answer_extraction._text_to_int("five"), 5)
    self.assertEqual(answer_extraction._text_to_int("twenty"), 20)

  def test_extract_count_eval(self):
    self.assertEqual(
        answer_extraction.extract_count_eval(
            "The words appear **[ 3 , 4 , 5 ]** times.", 3
        ),
        [3, 4, 5],
    )
    self.assertEqual(
        answer_extraction.extract_count_eval(
            "The words 'apple' appears **12** times in this sentence.", 1
        ),
        [12],
    )

  def test_extract_mathgap_eval(self):
    self.assertEqual(
        answer_extraction.mathgap_eval(
            "The answer is \\boxed{42}."
        ),
        42,
    )

  def test_extract_logic_eval(self):
    self.assertEqual(
        answer_extraction.extract_logic_eval(
            "The answer is: A."
        ),
        "A",
    )
    self.assertEqual(
        answer_extraction.extract_logic_eval(
            "The answer is: \\boxed{B}."
        ),
        "B",
    )
    self.assertEqual(
        answer_extraction.extract_logic_eval(
            "Final answer: C."
        ),
        "C",
    )

  def test_extract_unpuzzle_eval(self):
    self.assertEqual(
        answer_extraction.extract_unpuzzle_eval("The answer is: \\boxed{42}."),
        "42",
    )
    self.assertEqual(
        answer_extraction.extract_unpuzzle_eval("The answer is: 42."),
        "42",
    )
    self.assertEqual(
        answer_extraction.extract_unpuzzle_eval("**Answer: 42**"),
        "42",
    )


if __name__ == "__main__":
  absltest.main()
