"""Run overall and per-rule InkProof evaluation metrics."""

import json
from collections import defaultdict
from pathlib import Path

from app import engine

HERE = Path(__file__).resolve().parent

RULES = [
    {
        "id": "R-TERM-01",
        "name": "Hype terms",
        "kind": "term",
        "config": {
            "terms": {
                "guaranteed": "proven",
                "best in class": "strong",
                "world-class": "high-quality",
            }
        },
        "approved": True,
    },
    {
        "id": "R-CLM-03",
        "name": "Ranking claims",
        "kind": "rank",
        "config": {},
        "approved": True,
    },
    {
        "id": "R-NUM-01",
        "name": "Numerical claims",
        "kind": "num",
        "config": {},
        "approved": True,
    },
    {
        "id": "R-TON-02",
        "name": "Tone",
        "kind": "tone",
        "config": {},
        "approved": True,
    },
]

FACTS = [
    {
        "id": "F-012",
        "text": "Average score gain: 18% over an 8-week course",
        "keywords": ["score"],
        "value": 18,
        "unit": "%",
        "period": 8,
        "period_unit": "week",
        "cumulative": True,
        "rank": False,
        "valid_until": "2999-12-31",
        "approved": True,
    },
    {
        "id": "F-031",
        "text": "Average store rating: 4.6 stars",
        "keywords": ["rated", "rating"],
        "value": 4.6,
        "unit": "stars",
        "period": None,
        "period_unit": None,
        "cumulative": False,
        "rank": False,
        "valid_until": "2000-01-01",
        "approved": True,
    },
]


def calculate_metrics(tp, fp, fn, tn):
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = (
        2 * precision * recall / (precision + recall)
        if precision + recall
        else 0.0
    )

    return {
        "TP": tp,
        "FP": fp,
        "FN": fn,
        "TN": tn,
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
    }


def validate_dataset(rows):
    if len(rows) != 60:
        raise ValueError(f"Expected 60 examples; found {len(rows)}")

    known_rules = {rule["id"] for rule in RULES}
    seen_ids = set()

    for row in rows:
        required = {"id", "text", "should_flag", "reason", "rule_id"}
        missing = required - row.keys()

        if missing:
            raise ValueError(
                f"{row.get('id', 'Unknown')}: missing fields {sorted(missing)}"
            )

        if row["id"] in seen_ids:
            raise ValueError(f"Duplicate example ID: {row['id']}")

        seen_ids.add(row["id"])

        if not isinstance(row["should_flag"], bool):
            raise ValueError(f"{row['id']}: should_flag must be true or false")

        if row["rule_id"] not in known_rules:
            raise ValueError(
                f"{row['id']}: unknown rule ID {row['rule_id']}"
            )

    if len(seen_ids) != 60:
        raise ValueError("Dataset must contain 60 unique IDs")


def main():
    path = HERE / "labeled_examples.json"
    rows = json.loads(path.read_text(encoding="utf-8"))

    validate_dataset(rows)

    overall = [0, 0, 0, 0]
    per_rule = defaultdict(lambda: [0, 0, 0, 0])
    mismatches = []

    for row in rows:
        findings = engine.review(row["text"], RULES, FACTS)
        predicted_rules = {finding["rule_id"] for finding in findings}

        expected = row["should_flag"]
        predicted = bool(predicted_rules)

        if predicted and expected:
            overall[0] += 1
        elif predicted and not expected:
            overall[1] += 1
        elif not predicted and expected:
            overall[2] += 1
        else:
            overall[3] += 1

        rule_id = row["rule_id"]
        rule_predicted = rule_id in predicted_rules
        counts = per_rule[rule_id]

        if rule_predicted and expected:
            counts[0] += 1
        elif rule_predicted and not expected:
            counts[1] += 1
        elif not rule_predicted and expected:
            counts[2] += 1
        else:
            counts[3] += 1

        if predicted != expected or rule_predicted != expected:
            mismatches.append({
                "id": row["id"],
                "expected": expected,
                "predicted_rules": sorted(predicted_rules),
                "expected_rule": rule_id,
            })

    print("\nINKPROOF EVALUATION")
    print("=" * 50)
    print("Total examples:", len(rows))

    print("\nOVERALL METRICS")
    print(json.dumps(calculate_metrics(*overall), indent=2))

    print("\nPER-RULE METRICS")
    for rule in RULES:
        rule_id = rule["id"]
        counts = per_rule[rule_id]
        print(f"\n{rule_id} - {rule['name']}")
        print("Examples:", sum(counts))
        print(json.dumps(calculate_metrics(*counts), indent=2))

    print("\nVALIDATION")
    print("Mismatches:", len(mismatches))

    for mismatch in mismatches:
        print(mismatch)

    print(
        "\nNote: This is a synthetic regression dataset. "
        "These scores measure agreement with its labels, "
        "not independently validated production accuracy."
    )

    if mismatches:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
