# aspace-adk-recipes-adapter

Adapter A'Space pour `adk-recipes` (fork `Amdkn/adk-recipes`, gel `a93b9cc`,
Apache-2.0). Seul code A'Space du fork — le code amont est byte-identique
au gel (H-M2).

## Surface (contrat seul)

Validation locale de recettes, sans déployer ni exécuter aucune recette :

- `validate manifest <scope>` — valide `manifest.yaml`
- `validate structure <scope>` — valide la structure de la recette
- `validate readme <scope>` — valide le README
- `validate placement <scope>` — valide le placement de la recette
- `validate all <scope>` — toutes les vérifications

`scope` = `all` | `core` | `contrib` | `plugins` |
`core/<lang>/<recipe>` (ex. `core/python/rag-agent-search`).

Entrée : `tools/validate.py:main()` (ajouter `tools/` au `sys.path`).
Lecture seule sur disque, aucun appel réseau, aucun appel modèle.

## Jamais

- Déployer ou exécuter une recette (`uv run`, ADK, Gemini).
- Tout appel réseau au boot ou à la validation.
- Toute écriture hors du répertoire de sortie explicite.
- Définir `AQA_TRACES_GCS_BUCKET` ou `LOGS_BUCKET_NAME` (ces variables
  activent l'export télémétrie OpenTelemetry de deux recettes ;
  l'adapter les laisse absentes — voir `TELEMETRY-AUDIT`).

## Télémétrie

Aucun SDK tiers. OpenTelemetry confiné à deux recettes
(`ambient-quality-agent`, `genmedia-for-commerce`), off par défaut
(bucket GCS requis). Le token `gccl/` est une attribution dans un header
d'appel Gemini, pas un envoi séparé. Voir
`adk-recipes-TELEMETRY-AUDIT.md` (domicile V5).

## Smoke test

```sh
python3 -m pytest aspace-adk-recipes-adapter/smoke_test.py -q
```

Vérifie : gel ancêtre, seul l'adapter a changé depuis le gel, contrat,
variables télémétrie absentes, `validate manifest` + `validate structure`
sur `core/python/rag-agent-search` (0), rejet d'un scope inexistant (!= 0).
