#!/usr/bin/env python3
"""Validate a scene graph and run the five HORUS competency questions."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from validate import (
    DATA, ONTOLOGY, ROOT, SHAPES, read_graph, validate_graph, with_class_inheritance,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=DATA)
    parser.add_argument("--ontology", type=Path, default=ONTOLOGY)
    parser.add_argument("--shapes", type=Path, default=SHAPES)
    parser.add_argument("--questions", type=Path, default=ROOT / "competency-questions")
    parser.add_argument(
        "--check-example", action="store_true",
        help="Compare results with the recorded answers for example.ttl",
    )
    args = parser.parse_args()
    try:
        data = read_graph(args.data)
        ontology = read_graph(args.ontology)
        validate_graph(data, ontology, read_graph(args.shapes))
        graph = with_class_inheritance(data, ontology)
        questions = json.loads(
            (args.questions / "expected.json").read_text(encoding="utf-8")
        )
        if not questions:
            raise ValueError("No competency questions are defined.")
        failed = False
        for identifier, question in questions.items():
            query = (args.questions / "queries" / f"{identifier}.rq").read_text(
                encoding="utf-8"
            )
            result = graph.query(query)
            columns = [str(column) for column in result.vars]
            rows = sorted(tuple(str(cell) for cell in row) for row in result)
            print(f"{identifier}: {question['question']}")
            for row in rows:
                print("  " + " | ".join(row))
            if not rows:
                print("  No results.")
            if args.check_example:
                expected = sorted(tuple(row) for row in question["rows"])
                matches = columns == question["columns"] and rows == expected
                print("  PASS" if matches else f"  FAIL: expected {expected!r}")
                failed |= not matches
        return int(failed)
    except Exception as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
