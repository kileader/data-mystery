# Data Mystery

**Practice investigating a business problem with data, then compare your findings with a reproducible answer key.**

Data Mystery generates fictional business cases as related CSV tables, a briefing, and a data dictionary. Use Python, SQL, Excel, or another analysis tool to investigate the evidence and explain what happened. The solution stays in a separate folder until you choose to reveal it.

The first case, **Margin Mirage**, follows Northstar Market, an online retailer reporting deteriorating economics despite apparently healthy sales. Leadership has competing explanations. Your job is to identify what changed, quantify the damage, and recommend an action.

**Status:** early prototype, with one authored scenario and a working generation/investigation/reveal loop. All businesses, customers, and transactions are synthetic. Changing the seed creates different rows for the same underlying mystery; it does not create a new storyline.

## What you can practice

- Joining eight tables at different grains without double-counting financial amounts.
- Reconstructing contribution from sales, discounts, product costs, shipping, and refunds.
- Comparing time periods and segments to distinguish a major driver from a plausible distraction.
- Writing an evidence-backed explanation with assumptions and limitations.

The engineering premise is simple: author the causal story explicitly, generate consistent records with deterministic code, and check that the intended evidence is present. The runtime uses only the Python standard library; no API keys, hosted services, or LLM calls are required.

## Quick start

Python 3.11 or newer is required. Download or clone this repository, open a terminal in its root, and create a virtual environment.

**Windows PowerShell**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**macOS / Linux**

```sh
python3 -m venv .venv
source .venv/bin/activate
```

Then, on either platform:

```powershell
python -m pip install -e .
python -m datamystery new --output my-case --seed 20260314
```

Read `my-case/briefing.md` and `my-case/schema.md`, then investigate the files in `my-case/data/`. Start with the [investigation guide](docs/investigating.md) for table relationships and suggested deliverables without the solution.

When you have written your explanation, reveal the answer:

```powershell
python -m datamystery reveal my-case
```

The installed `datamystery` command is equivalent to `python -m datamystery`. Run `python -m datamystery --help` for help. Without `--output`, a new case is written to `margin-mirage-case`; the default seed is `20260314`. The generator refuses to overwrite a nonempty output directory, so use a new directory for another run.

If PowerShell blocks activation, use `.venv\Scripts\python.exe` in place of `python` in the remaining commands; activation is optional.

## Generated case

The default scenario contains 5,200 orders and 1,800 customers over January–June 2026, across eight CSV tables. Line-item, coupon, and refund counts vary by seed.

```text
my-case/
├── briefing.md         # Business question and requested deliverable
├── schema.md           # Table grains and financial definitions
├── manifest.json       # Seed, generator version, and SHA-256 hashes
├── data/               # Eight related CSV tables
└── .datamystery/        # Spoilers: scenario, answer key, and solution
```

**Spoiler note:** investigate the generated files first. The scenario source, analysis module, and tests also expose the answer. The hidden folder is an honor-system boundary, not access control.

Generated cases are local working artifacts. The documented output folders and hidden answer folders are excluded from Git; use `generated-cases/` for additional local runs.

## Share a case for an independent play-test

Give the player `briefing.md`, `schema.md`, `manifest.json`, `data/`, and a copy of [docs/investigating.md](docs/investigating.md). Keep `.datamystery/` and the repository source with the organizer. A dot-prefixed folder is not reliably hidden in Windows or editors; explicitly exclude it from the handoff.

For example, after generating `my-case`, run this from the repository root in PowerShell. Use a fresh destination for each handoff:

```powershell
New-Item -ItemType Directory -Path generated-cases/player-copy -ErrorAction Stop
Copy-Item my-case/briefing.md,my-case/schema.md,my-case/manifest.json generated-cases/player-copy/
Copy-Item my-case/data generated-cases/player-copy/data -Recurse
Copy-Item docs/investigating.md generated-cases/player-copy/investigating.md
```

Share only `generated-cases/player-copy/`. The player can use any analysis tool and needs no package installation. Keep the full original case and record `git rev-parse HEAD` alongside it (also note any uncommitted changes). After the player submits their findings, run `python -m datamystery reveal my-case` yourself and share the solution. The player-only copy deliberately has no reveal material.

## Scope and limitations

- This is a practice dataset generator, not a completed independent analysis or a model trained on real business data.
- The financial measure is contribution after product cost, shipping, and refunds. It excludes overhead and, by default, marketing spend; it is not operating profit.
- The data supports diagnosing patterns in transactions. The authored narrative contains background events that the CSV files alone cannot prove.
- The answer key uses known scenario dates and segments to summarize evidence; it does not independently discover causes or grade your submission. Evidence thresholds are enforced by the tests for the reference seed, not during every generation run.
- Tests verify repeatability, selected relationships and arithmetic, and evidence thresholds for the reference seed. They do not establish correctness for every seed or custom scenario configuration.
- Reproduce a case using the same seed and code revision, retaining the manifest to check CSV hashes. A seed alone is not a promise of identical output across future generator changes.

There is currently no web UI, automatic grading, or general-purpose scenario engine. The next useful milestone is an independent play-test to assess whether the briefing and visible evidence support a convincing investigation.

## Development

After the editable install above:

```sh
python -m unittest discover -s tests -v
```

GitHub Actions is configured to install the package, run the tests, and exercise generation and reveal on Windows and Linux with Python 3.11 and 3.14.

See [architecture](docs/architecture.md) for design boundaries and [contributing](CONTRIBUTING.md) for development and play-test feedback.
