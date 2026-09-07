The shapes check the subject and object types of the six HORUS relations.
Class inheritance is respected: an Agent satisfies an Entity requirement.

The validator also checks vocabulary names, instance types and references.
Instances use IRIs; labels and comments use literals. No minimum relation counts
or clinical workflow rules are imposed.

Run from the repository root:

```powershell
python scripts/ontology/validate.py
python scripts/ontology/validate.py --data path/to/scene.ttl
```
