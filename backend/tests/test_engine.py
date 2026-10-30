
from app import engine as eng

RULES = [
    {
        "id": "R-TERM-01",
        "name": "t",
        "kind": "term",
        "config": {"terms": {"guaranteed": "proven"}},
        "approved": True,
    },
    {"id": "R-CLM-03", "name": "r", "kind": "rank", "config": {}, "approved": True},
    {"id": "R-NUM-01", "name": "n", "kind": "num", "config": {}, "approved": True},
    {"id": "R-TON-02", "name": "o", "kind": "tone", "config": {}, "approved": True},
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
        "keywords": ["rated"],
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

TEXT = (
    "Northwind is India’s #1 learning app. Students raise their scores "
    "by 60% in just 2 weeks!!! Rated 4.6 stars by parents. Sign up now."
)


def by_label(findings):
    return {f["label"]: f for f in findings}


def test_northwind_example():
    findings = by_label(eng.review(TEXT, RULES, FACTS))
    assert findings["Unverified"]["status"] == "human"
    assert "Contradicts" not in findings
    assert findings["Expired"]["status"] == "human"
    assert findings["Tone"]["status"] == "confirmed"


def test_supported_claim_has_no_finding():
    assert eng.review(
        "Student scores rise 18% on average. Sign up.",
        RULES,
        FACTS,
    ) == []


def test_different_context_is_unverified_not_false():
    findings = eng.review("Scores rise 30% in 12 weeks.", RULES, FACTS)
    assert [item["label"] for item in findings] == ["Unverified"]


def test_unapproved_rule_cannot_confirm():
    rules = [
        dict(rule, approved=False) if rule["id"] == "R-TON-02" else rule
        for rule in RULES
    ]
    findings = by_label(eng.review("Great!! Sign up.", rules, FACTS))
    assert findings["Tone"]["status"] == "human"


def test_verifier_rejects_invented_quote_or_rule():
    bad = {
        "id": "AI-0",
        "rule_id": "R-FAKE",
        "fact_id": None,
        "label": "AI-suggested",
        "quote": "not in draft",
        "reason": "",
        "fix": None,
    }
    result = eng.verify(bad, TEXT, RULES, FACTS)
    assert not result["checks"]["rule"]
    assert not result["checks"]["quote"]
    assert result["status"] == "human"


def test_all_banned_term_occurrences_are_detected():
    findings = eng.review(
        "This guaranteed result is guaranteed.",
        RULES,
        FACTS,
    )
    banned = [item for item in findings if item["label"] == "Banned term"]

    assert len(banned) == 2
    assert [item["quote"] for item in banned] == ["guaranteed", "guaranteed"]


def test_multiple_numeric_claims_in_one_sentence():
    text = "Rated 4.6 stars by parents and scores improve 60% in 2 weeks."
    findings = eng.review(text, RULES, FACTS)

    numeric = [
        item for item in findings
        if item["rule_id"] == "R-NUM-01"
    ]

    assert len(numeric) == 2
    assert any(item["label"] == "Expired" for item in numeric)
    assert any(item["label"] == "Unverified" for item in numeric)


def test_multiple_numbers_in_one_sentence():
    text = "Our app has 4.6 stars and improves scores by 60% in 2 weeks."
    findings = eng.review(text, RULES, FACTS)

    numeric = [
        item for item in findings
        if item["rule_id"] == "R-NUM-01"
    ]

    assert len(numeric) >= 2
def test_prefers_approved_fact_with_current_source():
    old_fact = {
        "id": "F-012",
        "text": "Average score gain: 18% over 8 weeks",
        "keywords": ["score", "gain"],
        "value": 18,
        "unit": "%",
        "period": 8,
        "period_unit": "weeks",
        "cumulative": True,
        "rank": False,
        "valid_until": "2027-12-31",
        "approved": True,
        "version": 1,
        "sources": [],
    }

    sourced_fact = {
        **old_fact,
        "id": "F-7758A5CA6538",
        "sources": [{
            "filename": "inkproof-production-test.txt",
            "source_quote": "The average score gain was 18% over an 8-week course.",
            "stale": False,
        }],
    }

    selected = eng._select_numeric_fact(
        facts=[old_fact, sourced_fact],
        unit="%",
        sentence="our score gain was 18% in 8 weeks",
        value=18,
        period=8,
        claim_period_unit="weeks",
    )

    assert selected["id"] == "F-7758A5CA6538"