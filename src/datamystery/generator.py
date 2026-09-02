from __future__ import annotations

import csv
import hashlib
import json
import random
from datetime import date, timedelta
from pathlib import Path
from typing import Any, Iterable

from datamystery.analysis import analyze_case
from datamystery.case_spec import CaseSpec


PRODUCTS = (
    ("P001", "Noise-canceling headphones", "electronics", 210.00, 132.00),
    ("P002", "Mechanical keyboard", "electronics", 145.00, 86.00),
    ("P003", "Portable monitor", "electronics", 280.00, 190.00),
    ("P004", "Smart home hub", "electronics", 120.00, 72.00),
    ("P005", "Linen sheet set", "home", 125.00, 59.00),
    ("P006", "Pour-over coffee kit", "home", 78.00, 31.00),
    ("P007", "Desk lamp", "home", 92.00, 43.00),
    ("P008", "Storage bench", "home", 180.00, 91.00),
    ("P009", "Trail jacket", "apparel", 135.00, 58.00),
    ("P010", "Everyday sneakers", "apparel", 110.00, 46.00),
    ("P011", "Merino pullover", "apparel", 98.00, 39.00),
    ("P012", "Canvas backpack", "apparel", 84.00, 33.00),
)

TABLE_FIELDS = {
    "customers": ("customer_id", "signup_date", "region", "acquisition_channel"),
    "products": ("product_id", "product_name", "category", "list_price", "unit_cost"),
    "orders": (
        "order_id",
        "customer_id",
        "ordered_at",
        "marketing_channel",
        "shipping_zone",
        "order_status",
    ),
    "order_items": (
        "order_item_id",
        "order_id",
        "product_id",
        "quantity",
        "unit_price",
        "gross_sales",
        "discount_amount",
        "net_revenue",
        "unit_cost",
    ),
    "coupon_redemptions": ("redemption_id", "order_id", "coupon_code", "discount_amount"),
    "shipments": ("shipment_id", "order_id", "carrier", "shipped_at", "shipping_cost"),
    "refunds": ("refund_id", "order_id", "refund_date", "refund_amount", "reason"),
    "marketing_daily": ("date", "channel", "spend", "campaign_name"),
}


def generate_case(spec: CaseSpec, seed: int, output_dir: Path) -> dict[str, Any]:
    spec.validate()
    output_dir = output_dir.resolve()
    if output_dir.exists() and any(output_dir.iterdir()):
        raise FileExistsError(f"Output directory is not empty: {output_dir}")

    data_dir = output_dir / "data"
    hidden_dir = output_dir / ".datamystery"
    data_dir.mkdir(parents=True, exist_ok=True)
    hidden_dir.mkdir(parents=True, exist_ok=True)

    tables = _build_tables(spec, seed)
    for table_name, rows in tables.items():
        _write_csv(data_dir / f"{table_name}.csv", TABLE_FIELDS[table_name], rows)

    _write_text(output_dir / "briefing.md", _briefing_markdown(spec, seed))
    _write_text(output_dir / "schema.md", _schema_markdown())
    _write_json(hidden_dir / "case_spec.json", spec.to_dict())

    answer_key = analyze_case(
        output_dir,
        case_id=spec.case_id,
        incident_date=spec.generation["incident_date"],
        campaign_date=spec.generation["campaign_date"],
    )
    _write_json(hidden_dir / "answer_key.json", answer_key)
    _write_text(hidden_dir / "solution.md", _solution_markdown(spec, answer_key))

    file_hashes = {
        str(path.relative_to(output_dir)).replace("\\", "/"): _sha256(path)
        for path in sorted(data_dir.glob("*.csv"))
    }
    spec_bytes = json.dumps(spec.to_dict(), sort_keys=True, separators=(",", ":")).encode()
    manifest = {
        "case_id": spec.case_id,
        "title": spec.title,
        "difficulty": spec.difficulty,
        "seed": seed,
        "generator_version": 1,
        "case_spec_sha256": hashlib.sha256(spec_bytes).hexdigest(),
        "data_files": file_hashes,
    }
    _write_json(output_dir / "manifest.json", manifest)
    return manifest


def _build_tables(spec: CaseSpec, seed: int) -> dict[str, list[dict[str, Any]]]:
    rng = random.Random(seed)
    cfg = spec.generation
    start = date.fromisoformat(cfg["start_date"])
    end = date.fromisoformat(cfg["end_date"])
    incident = date.fromisoformat(cfg["incident_date"])
    campaign = date.fromisoformat(cfg["campaign_date"])
    ship_increase = date.fromisoformat(cfg["shipping_increase_date"])
    day_count = (end - start).days + 1

    customers: list[dict[str, Any]] = []
    for number in range(1, cfg["customer_count"] + 1):
        signup = start - timedelta(days=rng.randint(1, 500))
        customers.append(
            {
                "customer_id": f"C{number:05d}",
                "signup_date": signup.isoformat(),
                "region": rng.choices(
                    ["Northeast", "South", "Midwest", "West"], weights=[22, 34, 21, 23]
                )[0],
                "acquisition_channel": rng.choices(
                    ["organic", "paid_search", "email", "creator"], weights=[42, 27, 23, 8]
                )[0],
            }
        )

    products = [
        {
            "product_id": product_id,
            "product_name": name,
            "category": category,
            "list_price": f"{price:.2f}",
            "unit_cost": f"{cost:.2f}",
        }
        for product_id, name, category, price, cost in PRODUCTS
    ]
    products_by_category = {
        category: [product for product in PRODUCTS if product[2] == category]
        for category in ("electronics", "home", "apparel")
    }

    orders: list[dict[str, Any]] = []
    items: list[dict[str, Any]] = []
    redemptions: list[dict[str, Any]] = []
    shipments: list[dict[str, Any]] = []
    refunds: list[dict[str, Any]] = []
    redemption_number = refund_number = item_number = 0

    for order_number in range(1, cfg["order_count"] + 1):
        ordered = start + timedelta(days=rng.randrange(day_count))
        after_campaign = ordered >= campaign
        electronics_share = (
            cfg["campaign_electronics_share"] if after_campaign else cfg["base_electronics_share"]
        )
        category = rng.choices(
            ["electronics", "home", "apparel"],
            weights=[electronics_share, (1 - electronics_share) * 0.53, (1 - electronics_share) * 0.47],
        )[0]
        exploit_eligible = category == cfg["affected_category"] and ordered >= incident
        exploit_probability = cfg["stack_probability"] + (0.12 if after_campaign else -0.16)
        stacked = exploit_eligible and rng.random() < exploit_probability

        order_id = f"O{order_number:06d}"
        creator_weight = 38 if after_campaign and category == "electronics" else 7
        channel = rng.choices(
            ["organic", "paid_search", "email", "creator"],
            weights=[38, 29, 26, creator_weight],
        )[0]
        customer = rng.choice(customers)
        zone = rng.choices(["local", "regional", "national"], weights=[20, 48, 32])[0]
        orders.append(
            {
                "order_id": order_id,
                "customer_id": customer["customer_id"],
                "ordered_at": ordered.isoformat(),
                "marketing_channel": channel,
                "shipping_zone": zone,
                "order_status": "completed",
            }
        )

        selected_products = rng.sample(
            products_by_category[category], k=rng.choices([1, 2], [82, 18])[0]
        )
        selected_lines = [
            (product, 2 if rng.random() < 0.11 else 1) for product in selected_products
        ]
        gross_total = sum(product[3] * quantity for product, quantity in selected_lines)
        if stacked:
            codes_and_rates = [("CREATOR20", 0.20), ("SAVE15", 0.15)]
            if rng.random() < 0.48:
                codes_and_rates.append(("WELCOME10", 0.10))
        elif rng.random() < 0.24:
            codes_and_rates = [(rng.choice(["SAVE10", "WELCOME10", "LOYALTY10"]), 0.10)]
        else:
            codes_and_rates = []
        total_rate = sum(rate for _, rate in codes_and_rates)

        order_net = 0.0
        order_cost = 0.0
        for product, quantity in selected_lines:
            item_number += 1
            gross = product[3] * quantity
            discount = round(gross * total_rate, 2)
            net = round(gross - discount, 2)
            cost = product[4] * quantity
            order_net += net
            order_cost += cost
            items.append(
                {
                    "order_item_id": f"I{item_number:07d}",
                    "order_id": order_id,
                    "product_id": product[0],
                    "quantity": quantity,
                    "unit_price": f"{product[3]:.2f}",
                    "gross_sales": f"{gross:.2f}",
                    "discount_amount": f"{discount:.2f}",
                    "net_revenue": f"{net:.2f}",
                    "unit_cost": f"{product[4]:.2f}",
                }
            )

        for code, rate in codes_and_rates:
            redemption_number += 1
            redemptions.append(
                {
                    "redemption_id": f"R{redemption_number:07d}",
                    "order_id": order_id,
                    "coupon_code": code,
                    "discount_amount": f"{gross_total * rate:.2f}",
                }
            )

        base_shipping = {"local": 6.4, "regional": 8.7, "national": 12.2}[zone]
        carrier_multiplier = 1.13 if ordered >= ship_increase else 1.0
        shipping_cost = base_shipping * carrier_multiplier * rng.uniform(0.93, 1.08)
        shipped = ordered + timedelta(days=rng.choice([1, 1, 2, 2, 3]))
        shipments.append(
            {
                "shipment_id": f"S{order_number:06d}",
                "order_id": order_id,
                "carrier": rng.choices(["ParcelPro", "ShipRight"], weights=[68, 32])[0],
                "shipped_at": shipped.isoformat(),
                "shipping_cost": f"{shipping_cost:.2f}",
            }
        )

        refund_probability = (
            cfg["refund_probability_exploit"] if stacked else cfg["refund_probability_normal"]
        )
        if rng.random() < refund_probability:
            refund_number += 1
            refund_fraction = rng.choice([0.35, 0.5, 1.0]) if stacked else rng.choice([0.5, 1.0])
            refunds.append(
                {
                    "refund_id": f"F{refund_number:06d}",
                    "order_id": order_id,
                    "refund_date": (shipped + timedelta(days=rng.randint(4, 24))).isoformat(),
                    "refund_amount": f"{order_net * refund_fraction:.2f}",
                    "reason": rng.choices(
                        ["changed_mind", "not_as_expected", "damaged", "duplicate_order"],
                        weights=[42, 29, 18, 11] if stacked else [29, 37, 26, 8],
                    )[0],
                }
            )

    marketing: list[dict[str, Any]] = []
    for offset in range(day_count):
        current = start + timedelta(days=offset)
        for channel, baseline in (("paid_search", 1100), ("email", 280), ("creator", 180)):
            is_campaign = channel == "creator" and current >= campaign
            spend = baseline * (5.1 if is_campaign else 1.0) * rng.uniform(0.90, 1.10)
            marketing.append(
                {
                    "date": current.isoformat(),
                    "channel": channel,
                    "spend": f"{spend:.2f}",
                    "campaign_name": "CREATOR20 launch" if is_campaign else "always-on",
                }
            )

    return {
        "customers": customers,
        "products": products,
        "orders": orders,
        "order_items": items,
        "coupon_redemptions": redemptions,
        "shipments": shipments,
        "refunds": refunds,
        "marketing_daily": marketing,
    }


def _write_csv(path: Path, fieldnames: Iterable[str], rows: list[dict[str, Any]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def _write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_text(path: Path, value: str) -> None:
    path.write_text(value.rstrip() + "\n", encoding="utf-8")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _briefing_markdown(spec: CaseSpec, seed: int) -> str:
    return f"""# {spec.title}

**Difficulty:** {spec.difficulty.title()}<br>
**Case seed:** `{seed}`<br>
**Analysis window:** {spec.generation['start_date']} through {spec.generation['end_date']}

## Briefing

{spec.briefing}

## Deliverable

Prepare a concise explanation supported by calculations or charts. Address:

1. What changed, and approximately when?
2. Which segment or behavior explains most of the deterioration?
3. How did revenue or volume obscure the problem?
4. Which apparent explanation is real but insufficient?
5. What action would you recommend?

Document assumptions and limitations. All monetary fields are USD. Do not inspect `.datamystery/` until you are ready to reveal the answer.
"""


def _schema_markdown() -> str:
    return """# Data dictionary

Each CSV is at the grain described below. IDs are stable within this generated case.

## `customers.csv`

One row per customer. `acquisition_channel` is the channel credited when the customer first registered.

## `products.csv`

One row per product. `list_price` and `unit_cost` are per unit. Unit cost is the retailer's product cost and excludes fulfillment and shipping.

## `orders.csv`

One row per order. `marketing_channel` is the session attribution for that order. All dates are ISO-8601 calendar dates.

## `order_items.csv`

One row per order line. `gross_sales = quantity * unit_price`; `net_revenue = gross_sales - discount_amount`. `unit_cost` is per unit, so line product cost is `quantity * unit_cost`.

## `coupon_redemptions.csv`

One row per coupon code accepted on an order. An order can have zero, one, or more rows. Coupon discount amounts should reconcile to item discounts apart from possible cent-level rounding.

## `shipments.csv`

One row per order. `shipping_cost` is the amount paid by the retailer, not customer shipping revenue.

## `refunds.csv`

One row per refunded order. `refund_amount` reduces recognized economics for this exercise. Orders absent from this table had no refund in the observation window.

## `marketing_daily.csv`

One row per date and active marketing channel. Spend is not allocated to individual orders. `campaign_name` is the internal label supplied by marketing.

## Suggested financial measure

A useful first-pass contribution measure is:

`net revenue - product cost - shipping cost - refund amount`

Marketing spend is deliberately separate; state clearly whether and how you incorporate it.
"""


def _solution_markdown(spec: CaseSpec, metrics: dict[str, Any]) -> str:
    m = metrics["metrics"]
    return f"""# Solution: {spec.title}

## Ground truth

{spec.reveal_summary}

## Evidence generated in this instance

- Electronics discount rate moved from {m['pre_discount_rate']:.1%} before the incident to {m['post_discount_rate']:.1%} after it.
- {m['post_electronics_stack_share']:.1%} of post-incident electronics orders used multiple coupon codes, versus {m['other_stack_share']:.1%} for all other orders.
- Electronics contribution margin rate moved from {m['pre_margin_rate']:.1%} to {m['post_margin_rate']:.1%}.
- Average shipping cost rose from ${m['pre_shipping_per_order']:.2f} to ${m['post_shipping_per_order']:.2f} per order.
- Incremental shipping explains only {m['shipping_share_of_unit_decline']:.1%} of the per-order contribution decline.
- Daily electronics order volume after the creator campaign was {m['campaign_volume_ratio']:.2f} times its pre-incident level.
- Refund incidence among stacked orders was {m['stacked_refund_rate']:.1%}, compared with {m['normal_refund_rate']:.1%} for other orders.

## Interpretation

The carrier increase and creator campaign are both real, so a simple correlation can implicate either one. The decisive evidence is the order-level linkage: multiple coupon rows appear abruptly in the affected category, reconcile to unusually deep item discounts, and coincide with severely negative unit economics. The campaign amplified the bug by bringing in more exploit orders. Shipping moved in the wrong direction but is quantitatively insufficient.
"""
