"""Run a small, transparent regression set against InkProof's rule engine.

From backend/: python -m evaluation.run_evaluation
The dataset is a starter set, not an independently validated benchmark.
"""
import json
from pathlib import Path
from app import engine

HERE = Path(__file__).resolve().parent
RULES = [
    {"id":"R-TERM-01","name":"Avoid absolute or hype terms","kind":"term","config":{"terms":{"guaranteed":"proven","best in class":"strong","world-class":"high-quality"}},"approved":True},
    {"id":"R-CLM-03","name":"Ranking claims need a named, dated source","kind":"rank","config":{},"approved":True},
    {"id":"R-NUM-01","name":"Numbers must match an approved, current fact","kind":"num","config":{},"approved":True},
    {"id":"R-TON-02","name":"Tone","kind":"tone","config":{},"approved":True},
]
FACTS = [
    {"id":"F-012","text":"Average score gain: 18% over an 8-week course","keywords":["score"],"value":18,"unit":"%","period":8,"period_unit":"week","cumulative":True,"rank":False,"valid_until":"2999-12-31","approved":True},
    {"id":"F-031","text":"Average store rating: 4.6 stars","keywords":["rated","rating"],"value":4.6,"unit":"stars","period":None,"period_unit":None,"cumulative":False,"rank":False,"valid_until":"2000-01-01","approved":True},
]

def main():
    rows = json.loads((HERE / "labeled_examples.json").read_text(encoding="utf-8"))
    tp = fp = fn = tn = 0
    for row in rows:
        predicted = bool(engine.review(row["text"], RULES, FACTS))
        expected = row["should_flag"]
        if predicted and expected: tp += 1
        elif predicted and not expected: fp += 1
        elif not predicted and expected: fn += 1
        else: tn += 1
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    print(f"Examples: {len(rows)} | TP={tp} FP={fp} FN={fn} TN={tn}")
    print(f"Precision: {precision:.1%} | Recall: {recall:.1%}")
    print("Note: starter synthetic dataset; treat metrics as regression signals, not proof of production accuracy.")
    # Regression gate: don't silently allow total detection to collapse.
    if recall < 0.70:
        raise SystemExit("Evaluation gate failed: recall below 70% on the starter set.")

if __name__ == "__main__":
    main()
