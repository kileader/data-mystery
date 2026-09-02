from __future__ import annotations

import csv
import hashlib
import json
import shutil
import unittest
from collections import Counter
from pathlib import Path

from datamystery.analysis import analyze_case
from datamystery.cases.margin_mirage import build_spec
from datamystery.generator import generate_case


SEED = 20260314


def csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


class GenerationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.scratch = Path.cwd() / ".test-artifacts" / self._testMethodName
        if self.scratch.exists():
            shutil.rmtree(self.scratch)
        self.scratch.mkdir(parents=True)

    def tearDown(self) -> None:
        if self.scratch.exists():
            shutil.rmtree(self.scratch)

    def test_same_seed_produces_identical_visible_data(self) -> None:
        first_path = self.scratch / "first"
        second_path = self.scratch / "second"
        first_manifest = generate_case(build_spec(), SEED, first_path)
        second_manifest = generate_case(build_spec(), SEED, second_path)

        self.assertEqual(first_manifest, second_manifest)
        for relative_path, expected_hash in first_manifest["data_files"].items():
            actual_hash = hashlib.sha256((second_path / relative_path).read_bytes()).hexdigest()
            self.assertEqual(expected_hash, actual_hash)

    def test_relations_and_financial_fields_are_coherent(self) -> None:
        case_path = self.scratch / "case"
        generate_case(build_spec(), SEED, case_path)
        data = case_path / "data"

        customer_ids = {row["customer_id"] for row in csv_rows(data / "customers.csv")}
        product_ids = {row["product_id"] for row in csv_rows(data / "products.csv")}
        orders = csv_rows(data / "orders.csv")
        order_ids = {row["order_id"] for row in orders}
        items = csv_rows(data / "order_items.csv")

        self.assertTrue(all(row["customer_id"] in customer_ids for row in orders))
        self.assertTrue(all(row["order_id"] in order_ids for row in items))
        self.assertTrue(all(row["product_id"] in product_ids for row in items))
        self.assertEqual(
            order_ids,
            {row["order_id"] for row in csv_rows(data / "shipments.csv")},
        )
        self.assertTrue(
            all(
                row["order_id"] in order_ids
                for table in ("coupon_redemptions.csv", "refunds.csv")
                for row in csv_rows(data / table)
            )
        )
        self.assertTrue(
            all(
                abs(
                    float(row["gross_sales"])
                    - float(row["discount_amount"])
                    - float(row["net_revenue"])
                )
                < 0.011
                for row in items
            )
        )

        item_discounts: Counter[str] = Counter()
        coupon_discounts: Counter[str] = Counter()
        for row in items:
            item_discounts[row["order_id"]] += float(row["discount_amount"])
        for row in csv_rows(data / "coupon_redemptions.csv"):
            coupon_discounts[row["order_id"]] += float(row["discount_amount"])
        self.assertTrue(
            all(
                abs(item_discounts[order_id] - coupon_discounts[order_id]) <= 0.03
                for order_id in order_ids
            )
        )

    def test_generated_case_contains_the_intended_discoveries(self) -> None:
        spec = build_spec()
        thresholds = {finding.key: finding.minimum_strength for finding in spec.expected_findings}
        case_path = self.scratch / "case"
        generate_case(spec, SEED, case_path)
        metrics = analyze_case(
            case_path,
            case_id=spec.case_id,
            incident_date=spec.generation["incident_date"],
            campaign_date=spec.generation["campaign_date"],
        )["metrics"]

        self.assertGreaterEqual(
            metrics["post_discount_rate"] - metrics["pre_discount_rate"],
            thresholds["electronics_discount_jump"],
        )
        self.assertGreaterEqual(
            metrics["post_electronics_stack_share"], thresholds["stacking_concentration"]
        )
        self.assertGreaterEqual(
            metrics["pre_margin_rate"] - metrics["post_margin_rate"],
            thresholds["margin_collapse"],
        )
        self.assertLessEqual(
            metrics["shipping_share_of_unit_decline"], thresholds["shipping_insufficient"]
        )
        self.assertGreaterEqual(metrics["campaign_volume_ratio"], thresholds["volume_masking"])
        self.assertGreater(metrics["stacked_refund_rate"], metrics["normal_refund_rate"] * 2)

    def test_manifest_seed_and_hidden_spec_are_recorded(self) -> None:
        case_path = self.scratch / "case"
        generate_case(build_spec(), SEED, case_path)
        manifest = json.loads((case_path / "manifest.json").read_text(encoding="utf-8"))
        hidden_spec = json.loads(
            (case_path / ".datamystery" / "case_spec.json").read_text(encoding="utf-8")
        )
        self.assertEqual(SEED, manifest["seed"])
        self.assertEqual("coupon_stacking_bug", hidden_spec["primary_cause"])


if __name__ == "__main__":
    unittest.main()
