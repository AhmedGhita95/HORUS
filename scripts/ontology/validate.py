#!/usr/bin/env python3
"""Validate extracted HORUS RDF using the v6 vocabulary and SHACL shapes."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from pyshacl import validate as shacl_validate
from rdflib import Graph, Literal, OWL, RDF, RDFS, URIRef

ROOT = Path(__file__).resolve().parents[2]
ONTOLOGY = ROOT / "ontology/source/HORUS.owl"
DATA = ROOT / "competency-questions/example.ttl"
SHAPES = ROOT / "shapes/horus-shapes.ttl"


def read_graph(path: Path) -> Graph:
    fmt = "xml" if path.suffix.lower() in {".owl", ".rdf", ".xml"} else "turtle"
    return Graph().parse(
        data=path.read_bytes(), format=fmt, publicID=path.resolve().as_uri()
    )


def vocabulary_errors(data: Graph, ontology: Graph) -> list[str]:
    classes = {node for node in ontology.subjects(RDF.type, OWL.Class)
               if isinstance(node, URIRef)}
    properties = set(ontology.subjects(RDF.type, OWL.ObjectProperty))
    if not classes or not properties:
        raise ValueError("The ontology must define classes and object properties.")
    typed_nodes = {s for s, kind in data.subject_objects(RDF.type) if kind in classes}
    errors = set()
    for subject, predicate, value in data:
        if not isinstance(subject, URIRef):
            errors.add(f"Instance must have an IRI: {subject}")
        if subject not in typed_nodes:
            errors.add(f"Instance has no declared HORUS type: {subject}")
        if predicate == RDF.type:
            if value not in classes:
                errors.add(f"Unknown class: {value}")
        elif predicate in {RDFS.label, RDFS.comment}:
            if not isinstance(value, Literal):
                errors.add(f"Label or comment must be text: {subject}")
        elif predicate not in properties:
            errors.add(f"Unknown relation: {predicate}")
        elif value not in typed_nodes:
            errors.add(f"Relation references an untyped or missing instance: {value}")
    return sorted(errors)


def validate_graph(data: Graph, ontology: Graph, shapes: Graph) -> None:
    errors = vocabulary_errors(data, ontology)
    if errors:
        raise ValueError("\n".join(errors))
    # No domain/range inference: it could hide incorrectly typed endpoints.
    conforms, _, report = shacl_validate(
        data, shacl_graph=shapes, ont_graph=ontology, inference="none"
    )
    if not conforms:
        raise ValueError(str(report))


def with_class_inheritance(data: Graph, ontology: Graph) -> Graph:
    graph = ontology + data
    for instance, kind in data.subject_objects(RDF.type):
        for parent in ontology.transitive_objects(kind, RDFS.subClassOf):
            graph.add((instance, RDF.type, parent))
    return graph


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=DATA, help="Extracted RDF/Turtle")
    parser.add_argument("--ontology", type=Path, default=ONTOLOGY)
    parser.add_argument("--shapes", type=Path, default=SHAPES)
    args = parser.parse_args()
    try:
        data = read_graph(args.data)
        ontology = read_graph(args.ontology)
        validate_graph(data, ontology, read_graph(args.shapes))
    except Exception as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print(f"PASS: {args.data.name} conforms to HORUS v6.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
