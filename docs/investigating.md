# Investigating a case

This guide describes the workflow and data relationships without revealing the cause. Read the generated `briefing.md` and `schema.md` before starting. Those files, `manifest.json`, and `data/*.csv` are all you need alongside this guide; Python and the repository source are not required to investigate a shared case.

## Start with a question

Translate the briefing into measurable questions: how did sales and contribution change over time, where did the deterioration concentrate, and how much can each proposed explanation account for? Record your initial hypotheses before looking for supporting evidence.

You can work in a notebook, a SQL database, or a spreadsheet. No analysis tool is required by the generator. Keep your own queries, transformations, and calculations so another person can reproduce your findings.

## Understand the joins

| Table | Grain | Relationship |
| --- | --- | --- |
| `customers` | One customer | `customer_id` joins to many orders |
| `products` | One product | `product_id` joins to many order items |
| `orders` | One order | `order_id` is the order-level key |
| `order_items` | One order line | Many lines can belong to an order |
| `coupon_redemptions` | One accepted coupon on an order | Zero or more rows per order |
| `shipments` | One shipment per order | One-to-one with orders in this scenario |
| `refunds` | One refunded order | Zero or one row per order in this scenario |
| `marketing_daily` | One date and reported paid marketing channel | Compare with orders aggregated by date and `marketing_channel`; organic orders have no spend row |

Aggregate order items and coupon redemptions separately to the order grain before combining them. Joining both detail tables directly can multiply rows, inflating sales and discounts. Check row counts and totals before and after joins. Use left joins for optional records such as refunds.

Customer acquisition channel and order marketing channel describe different events. Do not treat them as interchangeable.

## Make financial definitions explicit

For each order, sum item net revenue and item product cost (`quantity * unit_cost`), then subtract its shipping cost and refund amount. Treat an absent refund as zero.

Item net revenue already subtracts discounts. Coupon redemptions help explain and reconcile those discounts; subtracting them again would count them twice.

State the denominator for any margin rate: contribution divided by gross sales differs from contribution divided by net revenue. The reveal uses gross sales. Marketing spend is separate; if you include it, aggregate to a compatible grain and explain the allocation.

Refund dates may follow the sales period. An order-cohort analysis attaches refunds to the original order date, while a calendar-period cash-flow view uses the refund date. Name your choice. The answer key uses order cohorts. Refunds have not already been deducted from item net revenue; the exercise does not model inventory recovery or reversal of product cost.

## Build an explanation

1. Validate keys, dates, missing values, and financial reconciliation.
2. Establish a time-series baseline for volume, revenue, and contribution.
3. Compare segments and investigate when their behavior diverges.
4. Quantify competing explanations instead of relying on correlations alone.
5. Write your findings before using `python -m datamystery reveal my-case`, substituting your generated case path. If someone supplied only the player files, ask them for the solution after submitting your findings.

A useful submission includes a concise conclusion, two or three supporting tables or charts, reproducible calculations, and a recommended action. Explain what the data shows, what remains an inference, and what additional operational evidence you would request.

After revealing, compare the evidence and reasoning, not just the wording. The fictional story supplies background context that transaction records may not establish independently.
