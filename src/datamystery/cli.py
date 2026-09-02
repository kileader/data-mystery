from __future__ import annotations

import argparse
import sys
from pathlib import Path

from datamystery.cases.margin_mirage import build_spec
from datamystery.generator import generate_case


DEFAULT_SEED = 20260314


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="datamystery", description="Generate reproducible data-analysis mysteries."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    new_parser = subparsers.add_parser("new", help="Generate a new case")
    new_parser.add_argument(
        "--output", type=Path, default=Path("margin-mirage-case"), help="Case output directory"
    )
    new_parser.add_argument("--seed", type=int, default=DEFAULT_SEED, help="Reproducible random seed")

    reveal_parser = subparsers.add_parser("reveal", help="Show a generated case's ground truth")
    reveal_parser.add_argument("case_dir", nargs="?", type=Path, default=Path("."))
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "new":
            manifest = generate_case(build_spec(), args.seed, args.output)
            print(f"Generated {manifest['title']} at {args.output.resolve()}")
            print(f"Seed: {manifest['seed']}")
            print(f"Start with: {args.output.resolve() / 'briefing.md'}")
        elif args.command == "reveal":
            solution = args.case_dir.resolve() / ".datamystery" / "solution.md"
            if not solution.is_file():
                raise FileNotFoundError(f"No generated case found at {args.case_dir.resolve()}")
            print(solution.read_text(encoding="utf-8"))
    except (FileExistsError, FileNotFoundError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc
