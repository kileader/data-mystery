# Data Mystery

Data Mystery is a CLI-first experiment for generating synthetic analysis cases. Each case contains player-visible CSV files and documentation, plus a hidden, reproducible ground truth.

The first case, **Margin Mirage**, asks why an online retailer's profit collapsed while revenue and order volume remained healthy.

## Quick start

Python 3.11 or newer is required. The runtime has no third-party dependencies.

```powershell
python -m pip install -e .
datamystery new --output .\my-case --seed 20260314
```

Investigate `my-case/briefing.md`, `my-case/schema.md`, and the files under `my-case/data/`. When you are ready:

```powershell
datamystery reveal .\my-case
```

The hidden files live under `.datamystery/`. Avoid opening that directory until you want the answer.

Without installing the package, use `python -m datamystery` with `PYTHONPATH=src`.

## Development

```powershell
$env:PYTHONPATH = "src"
python -m unittest discover -s tests -v
```

See [docs/architecture.md](docs/architecture.md) for the MVP boundaries and extension strategy.
