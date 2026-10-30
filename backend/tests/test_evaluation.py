
"""Regression tests for the InkProof starter evaluation dataset."""

import json
from pathlib import Path

from app import engine

EVALUATION_DIR = Path(__file__).resolve().parents[1] / "evaluation"

RULES = [
    {
        "id": "R-TERM-01",
        "name": "Avoid absolute or hype terms",
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
        "name": "Ranking claims need a source",
        "kind": "rank",
        "config": {},
        "approved": True,
    },
    {
        "id": "R-NUM-01",
        "name": "Numbers must match an approved fact",
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


def load_examples():
    path = EVALUATION_DIR / "labeled_examples.json"
    return json.loads(path.read_text(encoding="utf-8"))


def test_starter_dataset_has_20_examples():
    examples = load_examples()
    assert len(examples) == 20


def test_every_example_has_required_labels():
    for example in load_examples():
        assert "id" in example
        assert "text" in example
        assert isinstance(example["should_flag"], bool)
        assert "reason" in example


def test_starter_dataset_recall_does_not_drop_below_70_percent():
    examples = load_examples()

    true_positives = 0
    false_negatives = 0

    for example in examples:
        predicted = bool(
            engine.review(example["text"], RULES, FACTS)
        )
        expected = example["should_flag"]

        if predicted and expected:
            true_positives += 1
        elif not predicted and expected:
            false_negatives += 1

    recall = (
        true_positives / (true_positives + false_negatives)
        if true_positives + false_negatives
        else 0.0
    )

    assert recall >= 0.70, (
        f"Starter evaluation recall dropped to {recall:.1%}"
    )


def test_matching_approved_score_claim_is_not_flagged():
    findings = engine.review(
        "Students improve scores by 18% over an 8-week course.",
        RULES,
        FACTS,
    )
    assert findings == []


def test_expired_rating_claim_is_flagged():
    findings = engine.review(
        "Rated 4.6 stars by parents.",
        RULES,
        FACTS,
    )
    assert any(
        finding["label"] == "Expired"
        for finding in findings
    )
