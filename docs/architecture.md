# MVP architecture

## Goal

Prove one narrow loop: author a causal case, generate coherent data, investigate it without privileged information, and reveal a ground truth that the visible evidence supports.

## Components

- `case_spec.py` defines and validates the JSON-serializable contract between scenario authoring and data generation.
- `cases/margin_mirage.py` is the authored scenario. It contains the briefing, causal story, expected evidence, red herrings, and calibrated parameters.
- `generator.py` turns that specification and a seed into normalized CSV tables. It alone creates row-level facts and calculated financial fields.
- `analysis.py` calculates an answer-key summary directly from the generated rows. Tests use the same public calculations to verify that the case is solvable.
- `cli.py` exposes `new` and `reveal`.

## Scenario versus data-generation boundary

An eventual LLM may propose:

- the business question and briefing;
- causal events and their ordering;
- the affected segment and observable consequences;
- red herrings;
- generation parameters within a supported case template;
- the discoveries a valid solution should contain.

Deterministic code must own:

- primary and foreign keys;
- row counts and referential integrity;
- sampling from calibrated distributions;
- timestamps and temporal constraints;
- arithmetic such as discounts, revenue, cost, refunds, and margin;
- serialization and seed handling;
- checks that the intended signal survived random sampling.

The spec is therefore not an instruction to fabricate rows. It is a validated configuration for a known generator. New causal mechanisms should initially get explicit generator code rather than a universal simulation framework.

## Output boundary

Player-visible material sits at the case root:

```text
briefing.md
schema.md
manifest.json
data/*.csv
```

Privileged material sits in `.datamystery/`:

```text
case_spec.json
answer_key.json
solution.md
```

This is an honor-system boundary, not a security boundary. A future hosted version could keep privileged files server-side.

## Deliberate non-features

There is no LLM integration, database, web UI, plugin system, general-purpose causal graph engine, or solution grader. Those do not help validate the core premise yet. The next useful milestone is an independent play-test followed by tuning the evidence strength and briefing.
