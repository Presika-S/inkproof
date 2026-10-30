import json
from pathlib import Path

import pytest

from app import engine
from evaluation.run_evaluation import (
    FACTS,
    RULES,
    calculate_metrics,
    validate_dataset,
)

EVALUATION_DIR = Path(__file__).resolve().parents[1] / "evaluation"


def load_examples():
    path = EVALUATION_DIR / "labeled_examples.json"
    return json.loads(path.read_text(encoding="utf-8"))


def test_dataset_has_60_examples():
    examples = load_examples()
    assert len(examples) == 60


def test_every_example_has_required_labels():
    examples = load_examples()

    for example in examples:
        assert "id" in example
        assert "text" in example
        assert isinstance(example["should_flag"], bool)
        assert "reason" in example
        assert "rule_id" in example


def test_dataset_validation_passes():
    validate_dataset(load_examples())


def test_dataset_ids_are_unique():
    examples = load_examples()
    ids = [example["id"] for example in examples]
    assert len(ids) == len(set(ids))


def test_all_rule_ids_are_known():
    known_rules = {rule["id"] for rule in RULES}

    for example in load_examples():
        assert example["rule_id"] in known_rules


def test_evaluation_recall_is_at_least_70_percent():
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

    denominator = true_positives + false_negatives
    recall = true_positives / denominator if denominator else 0.0

    assert recall >= 0.70, f"Recall dropped to {recall:.1%}"


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
    assert any(finding["label"] == "Expired" for finding in findings)


@pytest.mark.parametrize(
    "tp,fp,fn,tn,expected_precision,expected_recall,expected_f1",
    [
        (8, 2, 2, 8, 0.8, 0.8, 0.8),
        (10, 0, 0, 10, 1.0, 1.0, 1.0),
        (0, 0, 0, 10, 0.0, 0.0, 0.0),
    ],
)
def test_metric_calculation(
    tp, fp, fn, tn,
    expected_precision, expected_recall, expected_f1
):
    result = calculate_metrics(tp, fp, fn, tn)

    assert result["precision"] == expected_precision
    assert result["recall"] == expected_recall
    assert result["f1"] == expected_f1
