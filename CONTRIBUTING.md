# Contributing

Data Mystery is an early prototype with one scenario. Focused bug reports and independent play-test feedback are especially useful.

## Play-test feedback

Investigate a fresh case before reading the scenario code or tests, which contain spoilers. Include the seed and code revision with feedback. Describe where the briefing or schema was unclear, which claims you could support from the CSVs, and whether the revealed explanation matched your evidence. Mark solution details as spoilers in issue titles or use a collapsed details section in the issue body.

## Local development

Use Python 3.11 or newer and a virtual environment, following the [README](README.md#quick-start).

```sh
python -m pip install -e .
python -m unittest discover -s tests -v
python -m datamystery new --output generated-cases/playtest --seed 20260314
python -m datamystery reveal generated-cases/playtest
```

Choose a fresh output path for each run; generation does not overwrite nonempty directories. Keep generated cases and personal analysis artifacts out of commits.

## Changes

Read the [architecture](docs/architecture.md) before extending the generator. Keep scenario authoring separate from row generation, and preserve explicit arithmetic and table relationships. The current generator and answer-key analysis contain scenario-specific assumptions; a new specification alone does not add support for an arbitrary causal mechanism.

For bug fixes, explain the failure and add a regression test when it protects meaningful behavior. For generation changes, verify financial reconciliation, relationships, reproducibility, and the intended evidence. Describe any expected changes to generated data or hashes in the pull request. Never submit credentials or real customer data.

The test suite uses Python's built-in `unittest`; no third-party test runner is required. GitHub Actions also checks the installed CLI on Windows and Linux.
