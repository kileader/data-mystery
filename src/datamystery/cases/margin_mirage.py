from datamystery.case_spec import CaseSpec, Effect, ExpectedFinding


def build_spec() -> CaseSpec:
    return CaseSpec(
        schema_version=1,
        case_id="margin-mirage",
        title="Margin Mirage",
        case_type="profit_decline",
        difficulty="medium",
        briefing=(
            "Northstar Market, a mid-sized online retailer, reported deteriorating contribution "
            "during Q2 2026 despite healthy merchandise revenue. The COO "
            "blames a March carrier price increase. Marketing points to its April campaign "
            "promoting the existing CREATOR20 code as evidence that its spending worked. "
            "Determine what principally damaged "
            "unit economics, when it began, which part of the business was most affected, and "
            "whether shipping is a sufficient explanation. Quantify your claims."
        ),
        primary_cause="coupon_stacking_bug",
        affected_segment="electronics",
        incident_date="2026-03-14",
        reveal_summary=(
            "A checkout release on March 14 accidentally allowed multiple promotion codes on "
            "electronics orders. Deal-focused creators spread the exploit in April, increasing "
            "volume enough to mask the collapsing unit margin. Deep discounts and a higher refund "
            "rate caused most of the damage. Shipping did become more expensive, but its per-order "
            "increase was too small to explain the loss."
        ),
        causal_graph=(
            Effect("checkout_release", "coupon_stacking", "enabled"),
            Effect("coupon_stacking", "electronics_discount_rate", "increased"),
            Effect("creator_campaign", "exploit_awareness", "increased"),
            Effect("exploit_awareness", "electronics_order_volume", "increased"),
            Effect("coupon_stacking", "unit_margin", "decreased"),
            Effect("exploit_orders", "refund_rate", "increased"),
            Effect("carrier_price_change", "shipping_cost_per_order", "slightly_increased"),
        ),
        expected_findings=(
            ExpectedFinding(
                "electronics_discount_jump",
                "Electronics discount rate rises sharply after March 14.",
                0.18,
            ),
            ExpectedFinding(
                "stacking_concentration",
                "Multi-code orders are concentrated in post-incident electronics.",
                0.55,
            ),
            ExpectedFinding(
                "margin_collapse",
                "Post-incident electronics contribution margin falls by at least 20 points.",
                0.20,
            ),
            ExpectedFinding(
                "shipping_insufficient",
                "Incremental shipping is less than one quarter of the contribution decline.",
                0.25,
            ),
            ExpectedFinding(
                "volume_masking",
                "Electronics order volume rises after the creator campaign.",
                1.35,
            ),
        ),
        red_herrings=(
            "A real carrier rate increase begins March 1.",
            "A creator marketing campaign begins April 1 and correlates with the decline.",
        ),
        generation={
            "start_date": "2026-01-01",
            "end_date": "2026-06-30",
            "order_count": 5200,
            "customer_count": 1800,
            "incident_date": "2026-03-14",
            "campaign_date": "2026-04-01",
            "shipping_increase_date": "2026-03-01",
            "affected_category": "electronics",
            "base_electronics_share": 0.25,
            "campaign_electronics_share": 0.48,
            "stack_probability": 0.72,
            "refund_probability_normal": 0.045,
            "refund_probability_exploit": 0.16,
        },
    )
