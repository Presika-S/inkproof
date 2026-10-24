
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
RANK_RE = re.compile(r"(#\s?1|number one|no\.\s?1)[^.!?]*", re.I)
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
    for s in re.split(r"(?<=[.!?])\s+", text):
        lo = s.lower()

        # Check ranking claims.
        rk = RANK_RE.search(s)
        if rk:
            rf = next(
                (
                    f
                    for f in facts
                    if f["rank"]
                    and any(k in lo for k in f["keywords"])
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

        # Check every numerical claim in the sentence.
        for nm in NUM_RE.finditer(s):
            v = float(nm.group(1))
            unit = "%" if nm.group(2) == "%" else "stars"
            p = float(nm.group(3)) if nm.group(3) else None
            claim_period_unit = nm.group(4)
            q = nm.group(0)

            f = next(
                (
                    x
                    for x in facts
                    if x["unit"] == unit
                    and any(k in lo for k in x["keywords"])
                ),
                None,
            )

            if not f:
                add(
                    "R-NUM-01",
                    "Unverified",
                    q,
                    "No approved fact covers this figure. "
                    "It is not proven false, so a reviewer decides.",
                )

            elif is_expired(f):
                add(
                    "R-NUM-01",
                    "Expired",
                    q,
                    f"{f['id']} expired on {f['valid_until']}, "
                    "so it cannot support this figure.",
                    None,
                    f["id"],
                )

            elif v == f["value"] and (
                not f["period"]
                or p is None
                or (
                    p == f["period"]
                    and (
                        claim_period_unit is None
                        or claim_period_unit.lower().rstrip("s")
                        == f["period_unit"].lower().rstrip("s")
                    )
                )
            ):
                # The figure matches the approved fact.
                pass

            elif (
                f["cumulative"]
                and p is not None
                and f["period"]
                and v > f["value"]
            ):
                # A larger number or shorter time period alone does not
                # prove a claim false. Ask for evidence instead.
                period_unit = claim_period_unit or f["period_unit"]

                add(
                    "R-NUM-01",
                    "Unverified",
                    q,
                    f"{f['id']}: {f['text']}. "
                    f"The claim states {_num(v)}{unit} over "
                    f"{_num(p)} {period_unit}(s), while the approved "
                    f"fact describes an average over "
                    f"{_num(f['period'])} {f['period_unit']}(s). "
                    "The available fact does not establish whether "
                    "this claim is true or false. Additional evidence "
                    "specific to this claim is required.",
                    None,
                    f["id"],
                )

            else:
                add(
                    "R-NUM-01",
                    "Unverified",
                    q,
                    f"{f['id']} covers a different value or context. "
                    "The available fact does not establish whether "
                    "this claim is true or false.",
                    None,
                    f["id"],
                )

    # Check excessive exclamation marks.
    for i, m in enumerate(re.finditer(r"!+", text)):
        if len(m.group(0)) > 1 or i > 0:
            add(
                "R-TON-02",
                "Tone",
                m.group(0),
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
            (x for x in facts if x["id"] == f.get("fact_id")),
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

    return {
        **f,
        "checks": checks,
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
