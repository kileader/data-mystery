from __future__ import annotations

import csv
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path
from typing import Any


def _read(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def analyze_case(
    case_dir: Path, *, case_id: str, incident_date: str, campaign_date: str
) -> dict[str, Any]:
    data = case_dir / "data"
    products = {row["product_id"]: row for row in _read(data / "products.csv")}
    orders = {row["order_id"]: row for row in _read(data / "orders.csv")}
    items = _read(data / "order_items.csv")
    shipments = {row["order_id"]: float(row["shipping_cost"]) for row in _read(data / "shipments.csv")}
    refund_rows = _read(data / "refunds.csv")
    refunds = {row["order_id"]: float(row["refund_amount"]) for row in refund_rows}
    coupon_counts = Counter(row["order_id"] for row in _read(data / "coupon_redemptions.csv"))

    by_order: dict[str, dict[str, Any]] = defaultdict(
        lambda: {"gross": 0.0, "discount": 0.0, "net": 0.0, "cost": 0.0, "categories": set()}
    )
    for item in items:
        summary = by_order[item["order_id"]]
        summary["gross"] += float(item["gross_sales"])
        summary["discount"] += float(item["discount_amount"])
        summary["net"] += float(item["net_revenue"])
        summary["cost"] += int(item["quantity"]) * float(item["unit_cost"])
        summary["categories"].add(products[item["product_id"]]["category"])

    incident = date.fromisoformat(incident_date)
    campaign = date.fromisoformat(campaign_date)
    records: list[dict[str, Any]] = []
    for order_id, order in orders.items():
        item_summary = by_order[order_id]
        ordered = date.fromisoformat(order["ordered_at"])
        contribution = (
            item_summary["net"]
            - item_summary["cost"]
            - shipments[order_id]
            - refunds.get(order_id, 0.0)
        )
        records.append(
            {
                "order_id": order_id,
                "date": ordered,
                "electronics": "electronics" in item_summary["categories"],
                "gross": item_summary["gross"],
                "discount": item_summary["discount"],
                "contribution": contribution,
                "shipping": shipments[order_id],
                "stacked": coupon_counts[order_id] > 1,
                "refunded": order_id in refunds,
            }
        )

    pre = [record for record in records if record["electronics"] and record["date"] < incident]
    post = [record for record in records if record["electronics"] and record["date"] >= incident]
    other = [record for record in records if not (record["electronics"] and record["date"] >= incident)]
    stacked = [record for record in records if record["stacked"]]
    normal = [record for record in records if not record["stacked"]]

    def ratio_total(rows: list[dict[str, Any]], numerator: str, denominator: str) -> float:
        return sum(row[numerator] for row in rows) / sum(row[denominator] for row in rows)

    def average(rows: list[dict[str, Any]], key: str) -> float:
        return sum(row[key] for row in rows) / len(rows)

    pre_contribution = average(pre, "contribution")
    post_contribution = average(post, "contribution")
    pre_shipping = average(pre, "shipping")
    post_shipping = average(post, "shipping")
    pre_days = (incident - min(record["date"] for record in records)).days
    campaign_days = (max(record["date"] for record in records) - campaign).days + 1
    pre_daily_electronics = len(pre) / pre_days
    campaign_electronics = [
        record for record in records if record["electronics"] and record["date"] >= campaign
    ]

    metrics = {
        "pre_discount_rate": ratio_total(pre, "discount", "gross"),
        "post_discount_rate": ratio_total(post, "discount", "gross"),
        "post_electronics_stack_share": sum(row["stacked"] for row in post) / len(post),
        "other_stack_share": sum(row["stacked"] for row in other) / len(other),
        "pre_margin_rate": ratio_total(pre, "contribution", "gross"),
        "post_margin_rate": ratio_total(post, "contribution", "gross"),
        "pre_shipping_per_order": pre_shipping,
        "post_shipping_per_order": post_shipping,
        "shipping_share_of_unit_decline": max(post_shipping - pre_shipping, 0)
        / (pre_contribution - post_contribution),
        "campaign_volume_ratio": (len(campaign_electronics) / campaign_days) / pre_daily_electronics,
        "stacked_refund_rate": sum(row["refunded"] for row in stacked) / len(stacked),
        "normal_refund_rate": sum(row["refunded"] for row in normal) / len(normal),
        "order_count": len(records),
    }
    return {"case_id": case_id, "metrics": metrics}
