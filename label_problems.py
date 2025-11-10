#!/usr/bin/env python3
"""
label_problems.py

Reads every JSON file in folders matching "*_problems", uses GPT-4.1 with
Structured Outputs to label each problem with 'subjects' and 'topics', and
writes the updated JSON back in-place.
"""

import os
import json
import glob
from dotenv import load_dotenv
from tqdm import tqdm
from openai import OpenAI

# 1) Load API key from .env or environment
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise EnvironmentError("Please set OPENAI_API_KEY in your environment or .env file")

client = OpenAI()  # uses OPENAI_API_KEY env var

# 2) System prompt (as revised above)
SYSTEM_PROMPT = """
You are a mathematician who will label AMC and AIME-style High School Math problems with their subjects and topics. A subject is one of Arithmetic,  Algebra, Geometry, Counting, Probability, and Number Theory. A topic is a more detailed knowledge within a topic. A list of allowed topics and subjects can be found below in the schema.
You will be given a math problem. Following the schema below, output an array of one or more subjects and another array or one or more topics with no repeats, from the given list. Use your best judgment as to which ones best represent the knowledge required in the problem. Only include the main subjects and topics necessary to solve the problem.
You must output only a JSON object that adheres exactly to the provided JSON Schema (strict mode). Do not emit any other keys or prose.
"""

# 3) JSON Schema for structured outputs
SCHEMA = {
    "title": "MathProblemLabels",
    "type": "object",
    "properties": {
        "subjects": {
            "type": "array",
            "description": "List of main subjects relevant to the problem (no duplicates).",
            "items": {
                "type": "string",
                "enum": [
                    "Arithmetic",
                    "Algebra",
                    "Geometry",
                    "Counting",
                    "Probability",
                    "NumberTheory",
                ],
            },
            "minItems": 1,
        },
        "topics": {
            "type": "array",
            "description": "List of detailed topics required (no duplicates).",
            "items": {
                "type": "string",
                "enum": [
                    "Polynomials",
                    "Trigonometry",
                    "Inequalities",
                    "Logarithms",
                    "Functions",
                    "Triangles",
                    "Circles",
                    "CoordinateGeometry",
                    "3DGeometry",
                    "Permutations",
                    "Combinations",
                    "InclusionExclusion",
                    "Casework",
                    "ClassicalProbability",
                    "ConditionalProbability",
                    "ExpectedValue",
                    "GeometricProbability",
                    "ModularArithmetic",
                    "Divisibility",
                    "Primes",
                    "Diophantine",
                ],
            },
            "minItems": 1,
        },
    },
    "required": ["subjects", "topics"],
    "additionalProperties": False,
}


def label_problem(question: str) -> dict:
    """Call OpenAI to label a single question."""
    response = client.responses.create(
        # model="gpt-4.1-2025-04-14",
        model="gpt-4.1-nano-2025-04-14",
        input=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Label the following problem:\n\n{question}"},
        ],
        text={
            "format": {
                "type": "json_schema",
                "name": "math_problem_subjects",
                "schema": SCHEMA,
                "strict": True,
            }
        },
    )
    # The model’s raw JSON output
    raw = response.output_text
    return json.loads(raw)


def process_file(path: str) -> None:
    """Load a JSON file, label each problem, and overwrite it."""
    with open(path, "r") as f:
        problems = json.load(f)

    for idx, prob in enumerate(problems, 1):
        # skip if already labeled
        if "Subjects" in prob and "Topics" in prob:
            continue

        labels = label_problem(prob["Question"])
        prob["Subjects"] = labels["subjects"]
        prob["Topics"] = labels["topics"]
        print(f"  ↳ Labeled problem {idx}/{len(problems)}")

    # write back
    with open(path, "w") as f:
        json.dump(problems, f, indent=2)
    print(f"✔ Updated {path}\n")


def main():
    base = os.getcwd()
    json_paths = []

    # Walk every subdirectory looking for *.json
    for root, _, files in os.walk(base):
        if "_problems" in root:
            for fn in files:
                if fn.lower().endswith(".json"):
                    json_paths.append(os.path.join(root, fn))

    # Define priority order
    priorities = [
        ("aime_problems", 0),
        (os.path.join("amc_problems", "12A"), 1),
        (os.path.join("amc_problems", "12B"), 2),
        (os.path.join("amc_problems", "10A"), 3),
        (os.path.join("amc_problems", "10B"), 4),
        (os.path.join("amc_problems", "8"), 5),
        ("ahsme_problems", 6),
    ]

    def sort_key(path):
        for prefix, prio in priorities:
            if prefix in path:
                return (prio, path)
        # everything else last
        return (99, path)

    # Sort according to our custom key
    json_paths.sort(key=sort_key)

    print(f"Found {len(json_paths)} JSON files under '*_problems' folders.\n")
    for path in tqdm(json_paths, desc="Processing files"):
        process_file(path)


if __name__ == "__main__":
    main()
