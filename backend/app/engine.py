
"""Rule engine: propose findings and independently verify them.
Unsupported claims are not automatically treated as false.
Pure functions on plain dicts so they are easy to test.
"""

import re
from datetime import date

NUM_RE = re.compile(
    r"(\d+(?:\.\d+)?)\s*(%|stars?)(?:\s+in\s+(?:just\s+)?(\d+)\s*(week|day|month)s?)?",
    re.I,
)

RANK_RE = re.compile(
    r"(#\s?1|number one|no\.?\s?1)[^.!?]*",
    re.I,
)

NEEDS_HUMAN_LABELS = {"Unverified", "Expired", "AI-suggested"}


def is_expired(fact: dict, today: str | None = None) -> bool:
    return fact["valid_until"] < (today or date.today().isoformat())


def _num(x: float) -> str:
    return str(int(x)) if float(x).is_integer() else str(x)


def candidates(text: str, rules: list[dict], facts: list[dict]) -> list[dict]:
    out: list[dict] = []

    def add(rule_id, label, quote, reason, fix=None, fact_id=None):
        out.append(
            dict(
                id=f"{rule_id}-{len(out)}",
                rule_id=rule_id,
                label=label,
                quote=quote,
                reason=reason,
                fix=fix,
                fact_id=fact_id,
            )
        )

    # Detect every occurrence of every configured banned term.
    for r in rules:
        if r["kind"] == "term":
            for term, repl in r["config"].get("terms", {}).items():
                for m in re.finditer(re.escape(term), text, re.I):
                    add(
                        r["id"],
                        "Banned term",
                        m.group(0),
                        f"“{m.group(0)}” is an absolute or hype term.",
                        repl,
                    )

    # Review claims sentence by sentence.
    for sentence in re.split(r"(?<=[.!?])\s+", text):
        lo = sentence.lower()

        # Check ranking claims.
        rk = RANK_RE.search(sentence)
        if rk:
            rf = next(
                (
                    fact
                    for fact in facts
                    if fact["rank"]
                    and any(k in lo for k in fact["keywords"])
                ),
                None,
            )

            if not rf:
                add(
                    "R-CLM-03",
                    "Unverified",
                    rk.group(0),
                    "No approved source for this ranking. "
                    "It is not proven false, so a reviewer decides.",
                )
            elif is_expired(rf):
                add(
                    "R-CLM-03",
                    "Expired",
                    rk.group(0),
                    f"{rf['id']} expired on {rf['valid_until']}.",
                    None,
                    rf["id"],
                )

        # Check numerical claims.
        for nm in NUM_RE.finditer(sentence):
            value = float(nm.group(1))
            unit = "%" if nm.group(2) == "%" else "stars"
            period = float(nm.group(3)) if nm.group(3) else None
            claim_period_unit = nm.group(4)
            quote = nm.group(0)

            fact = next(
                (
                    item
                    for item in facts
                    if item["unit"] == unit
                    and any(k in lo for k in item["keywords"])
                ),
                None,
            )

            if not fact:
                add(
                    "R-NUM-01",
                    "Unverified",
                    quote,
                    "No approved fact covers this figure. "
                    "It is not proven false, so a reviewer decides.",
                )

            elif is_expired(fact):
                add(
                    "R-NUM-01",
                    "Expired",
                    quote,
                    f"{fact['id']} expired on {fact['valid_until']}, "
                    "so it cannot support this figure.",
                    None,
                    fact["id"],
                )

            elif value == fact["value"] and (
                not fact["period"]
                or period is None
                or (
                    period == fact["period"]
                    and (
                        claim_period_unit is None
                        or claim_period_unit.lower().rstrip("s")
                        == fact["period_unit"].lower().rstrip("s")
                    )
                )
            ):
                # The figure matches the approved fact.
                pass

            elif (
                fact["cumulative"]
                and period is not None
                and fact["period"]
                and value > fact["value"]
            ):
                period_unit = claim_period_unit or fact["period_unit"]

                add(
                    "R-NUM-01",
                    "Unverified",
                    quote,
                    f"{fact['id']}: {fact['text']}. "
                    f"The claim states {_num(value)}{unit} over "
                    f"{_num(period)} {period_unit}(s), while the approved "
                    f"fact describes an average over "
                    f"{_num(fact['period'])} {fact['period_unit']}(s). "
                    "The available fact does not establish whether "
                    "this claim is true or false. Additional evidence "
                    "specific to this claim is required.",
                    None,
                    fact["id"],
                )

            else:
                add(
                    "R-NUM-01",
                    "Unverified",
                    quote,
                    f"{fact['id']} covers a different value or context. "
                    "The available fact does not establish whether "
                    "this claim is true or false.",
                    None,
                    fact["id"],
                )

    # Check excessive exclamation marks.
    for i, match in enumerate(re.finditer(r"!+", text)):
        if len(match.group(0)) > 1 or i > 0:
            add(
                "R-TON-02",
                "Tone",
                match.group(0),
                "Only one exclamation mark is allowed, "
                "and none inside a claim.",
                ".",
            )

    return out


def verify(
    f: dict,
    text: str,
    rules: list[dict],
    facts: list[dict],
) -> dict:
    rule = next(
        (r for r in rules if r["id"] == f.get("rule_id")),
        None,
    )

    fact = (
        next(
            (item for item in facts if item["id"] == f.get("fact_id")),
            None,
        )
        if f.get("fact_id")
        else None
    )

    checks = {
        "rule": bool(rule and rule["approved"]),
        "quote": bool(f.get("quote")) and f["quote"] in text,
        "fact": (
            True
            if not f.get("fact_id")
            else bool(
                fact
                and fact["approved"]
                and not is_expired(fact)
            )
        ),
        "context": (
            True
            if not fact
            else any(k in text.lower() for k in fact["keywords"])
        ),
    }

    confirmed = (
        all(checks.values())
        and f["label"] not in NEEDS_HUMAN_LABELS
    )

    # Improvement 2: expose the evidence behind every finding.
    if fact:
        if is_expired(fact):
            evidence_status = "expired"
        elif not fact["approved"]:
            evidence_status = "unapproved"
        else:
            evidence_status = "linked"

        evidence = {
            "status": evidence_status,
            "fact_id": fact["id"],
            "text": fact["text"],
            "version": fact.get("version"),
            "approved": fact["approved"],
            "valid_until": fact["valid_until"],
            "expired": is_expired(fact),
        }
    else:
        evidence = {
            "status": "missing",
            "fact_id": None,
            "text": None,
            "version": None,
            "approved": False,
            "valid_until": None,
            "expired": False,
        }

    return {
        **f,
        "checks": checks,
        "evidence": evidence,
        "status": "confirmed" if confirmed else "human",
    }


def review(
    text: str,
    rules: list[dict],
    facts: list[dict],
) -> list[dict]:
    return [
        verify(candidate, text, rules, facts)
        for candidate in candidates(text, rules, facts)
    ]
