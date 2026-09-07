The five questions come from Section E of [HORUS.md](../docs/HORUS.md#e-query).
Their SPARQL queries are in `queries/`, and the example answers are in
`expected.json`. `example.ttl` represents the description in Section A.1.

```powershell
python scripts/ontology/run_competency_questions.py
python scripts/ontology/run_competency_questions.py --check-example
python scripts/ontology/run_competency_questions.py --data path/to/scene.ttl
```

The runner validates the input and applies class inheritance before querying.
`--check-example` compares answers with the supplied example; omit it for other scenes.
