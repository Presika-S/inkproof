# InkProof: Evidence-Backed Brand Governance

*Words verified. Decisions accountable.*

**Team NOVARA | FutureStack Round 3 Submission**

---

## Project Resources

| Resource | Link |
|---|---|
| Live application | https://inkproof.vercel.app/ |
| API documentation (Swagger) | https://inkproof-api.onrender.com/docs |
| Backend health check | https://inkproof-api.onrender.com/healthz |
| Source code | https://github.com/Presika-S/inkproof |

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Problem Statement](#2-problem-statement)
3. [Solution Overview](#3-solution-overview)
4. [Core Features](#4-core-features)
5. [Round 3 Deliverables](#5-round-3-deliverables)
6. [Evaluation Results](#6-evaluation-results)
7. [Illustrative Example](#7-illustrative-example)
8. [Technical Architecture](#8-technical-architecture)
9. [Testing and Verification](#9-testing-and-verification)
10. [Local Setup](#10-local-setup)
11. [Demo Access](#11-demo-access)
12. [Known Limitations](#12-known-limitations)
13. [Product Roadmap](#13-product-roadmap)
14. [Conclusion](#14-conclusion)

---

## 1. Executive Summary

InkProof is an evidence-backed brand-governance application. It connects brand rules, approved facts, evidence sources and human review in a single workflow. Teams can examine draft communications, identify potentially unsupported claims, understand why each finding was raised, inspect the supporting evidence, and record accountable review decisions.

The product is built on three principles:

- A suggestion is not a confirmation.
- Missing evidence is not proof that a claim is false.
- Important decisions require a recorded reason and an evidence trail.

InkProof is intended for marketing teams, content writers, advertising agencies, brand managers and compliance reviewers.

## 2. Problem Statement

Content is produced quickly, but brand verification is often manual and poorly documented. Organisations commonly face the following problems:

- Unsupported numerical claims enter published campaigns.
- Ranking and superiority statements are published without suitable sources.
- Approved facts become outdated without detection.
- Reviewers repeatedly search for the same supporting information.
- Automated writing tools suggest content without establishing whether it is supported.
- Review decisions cannot be traced when the reason and evidence are not recorded.

Traditional brand guidelines state what should be communicated but do not help verify whether a specific statement is supported.

## 3. Solution Overview

InkProof links each review to the relevant rules, quoted text, approved facts and verification checks, while keeping final decisions with human reviewers. The product follows a writer-to-reviewer workflow.

```text
                 WRITER
                   |
               Sign in
                   |
          Prepare content draft
                   |
              Intent Card
       Claims | Facts | Call to action
                   |
               Run review
                   |
             REVIEW ENGINE
                   |
       +-----------+-----------+
       |           |           |
    Hype terms   Rankings   Numerical
       |           |         claims
       +-----------+-----------+
                   |
          Independent verifier
                   |
       Check rule, quote, fact,
       approval and relevant context
                   |
             Findings cards
                   |
          Writer inspects results
                   |
          Submit for review
                   |
             REVIEWER
                   |
        Inspect findings and facts
                   |
        Uphold / Waive with reason
                   |
         Approve / Request changes
                   |
          Recorded review history
```

### Workflow Steps

1. **Sign in.** Writers and reviewers access the application under assigned roles.
2. **Prepare content.** Writers enter content or import a Word document.
3. **Define intent.** The Intent Card captures key facts, claims and calls to action.
4. **Run review.** The rule engine checks the content against configured brand rules.
5. **Verify findings.** The backend independently checks the rule, quotation, supporting fact and relevant context.
6. **Inspect evidence.** Writers see why a finding was raised and what information supports it.
7. **Submit for review.** The writer sends the draft to the reviewer workflow.
8. **Record decisions.** Reviewers examine findings and record decisions, with reasons where required.
9. **Finalise.** The reviewer approves the draft or requests changes.

Optional AI review can propose additional findings. AI suggestions are not treated as authoritative evidence, and backend verification remains required.

## 4. Core Features

### 4.1 Writer Workspace

- Sign-in with role-based access.
- Content preparation for social posts, web pages and emails.
- DOCX document import.
- Intent Card for claims, facts and calls to action.
- Review results and draft management.

### 4.2 Rule-Based Content Review

| Rule ID | Purpose |
|---|---|
| R-TERM-01 | Avoid absolute or hype terms |
| R-CLM-03 | Require a named, dated source for ranking claims |
| R-NUM-01 | Check numerical claims against approved, current facts |
| R-TON-02 | Apply tone and exclamation-mark restrictions |

### 4.3 Independent Verification

Each finding is checked against the following criteria:

- The rule is approved.
- The quoted text appears in the draft.
- The supporting fact is approved.
- The fact is current and relevant.
- The available context supports the finding.

This separates confirmed rule issues from claims that require further human investigation.

### 4.4 Evidence-Aware Finding Cards

Each finding card can display:

- Rule identifier and explanation.
- Quoted passage.
- Supporting fact and fact identifier.
- Evidence status and fact version.
- Approval and expiry information.
- Suggested edit, where applicable.

Suggested edits are never applied silently.

### 4.5 Evidence-Source Ingestion and Provenance

InkProof supports the following capabilities:

- Uploading and retrieving evidence documents.
- Maintaining document versions.
- Creating, listing and filtering evidence proposals, including pending proposals.
- Reviewer approval or rejection of proposals.
- Linking approved facts to source material.
- Retrieving source quotations and document-version details.
- Exposing stale-status information.

**Evidence lifecycle:**

> Source document → Upload → Evidence proposal → Human review → Approved fact → Source provenance → Content verification

### 4.6 Reviewer Workspace

- View submitted drafts and inspect individual findings.
- Uphold or waive findings, with written reasons for waivers.
- Approve drafts or request changes.
- Authors are prevented from reviewing or approving their own drafts.

### 4.7 Audit History and Governance

- Append-only event records.
- Before-and-after values for relevant changes.
- Actor and timestamp information.
- Recorded review decisions.
- Fact-change history exposed through the insights API.

### 4.8 Evaluation and Rule Health

A labelled regression dataset and evaluation runner measure rule behaviour against known examples. Overall and per-rule metrics are reported so that regressions can be identified as the product evolves.

---

## 5. Round 3 Deliverables

Round 2 established the core application and review workflow. Round 3 strengthened it in three committed areas.

### 5.1 Persistent Data and Stronger Governance

| Round 2 commitment | Round 3 implementation |
|---|---|
| Managed PostgreSQL | Not yet delivered (see Section 12) |
| Schema migrations | Not yet delivered (see Section 12) |
| Backups and tested restoration | Not yet delivered (see Section 12) |
| Finer-grained permissions | Writer and reviewer permission checks; prevention of self-review and self-approval |
| Append-only decision history | Append-only audit events with before-and-after values, actor and timestamp context, fact-change and review-decision history, and an insights/history API |

**Impact:** Review decisions are accountable, and changes can be investigated rather than treated as invisible updates.

### 5.2 Evidence-Source Ingestion

| Round 2 commitment | Round 3 implementation |
|---|---|
| Upload and version source documents | Evidence document upload, retrieval and version information |
| Link facts to their sources | Fact-to-source lookup, source quotations and version details |
| Detect stale or conflicting evidence | Stale-status information (conflict detection planned) |
| Require human approval of extracted facts | Proposal creation, pending-proposal workflow, reviewer approval and rejection |

**Impact:** Reviewers can inspect where a supporting fact originated and decide whether to trust it before it is used in content review.

### 5.3 Measurable Review Quality and Collaboration

| Round 2 commitment | Round 3 implementation |
|---|---|
| Labelled evaluation dataset | Expanded 60-example labelled regression dataset |
| Precision and recall per rule | Evaluation runner with overall and per-rule metrics |
| Regression tests | Automated regression tests; 22 passing backend tests |
| Reviewer assignment, notifications, workflow integrations | Reviewer queue and human decision workflow delivered; assignment, notifications and integrations remain planned |

**Impact:** Review behaviour can be measured and checked as the code changes, rather than relying solely on manual demonstration.

---

## 6. Evaluation Results

The evaluation runner processes 60 labelled examples across the four rule families.

### Overall Results

| Metric | Result |
|---|---:|
| Total examples | 60 |
| True positives | 32 |
| False positives | 0 |
| False negatives | 0 |
| True negatives | 28 |
| Precision | 100% |
| Recall | 100% |
| F1 score | 100% |
| Label mismatches | 0 |

### Per-Rule Results

| Rule | Examples | TP | FP | FN | TN |
|---|---:|---:|---:|---:|---:|
| R-TERM-01 | 16 | 11 | 0 | 0 | 5 |
| R-CLM-03 | 12 | 7 | 0 | 0 | 5 |
| R-NUM-01 | 15 | 9 | 0 | 0 | 6 |
| R-TON-02 | 17 | 5 | 0 | 0 | 12 |

> **Note:** The dataset is synthetic. These scores measure agreement with its labels and do not represent independently validated production accuracy. Per-rule metrics are calculated on the examples assigned to each rule.

---

## 7. Illustrative Example

**Approved fact:** Average score gain: 18% over an 8-week course.

**Case A: unsupported claim**

> Draft: "Our average score gain was 60% in just 2 weeks."

InkProof identifies a numerical claim and compares it with the approved fact. The finding explains that the approved fact describes an 18% average gain over eight weeks and does not establish a 60% gain over two weeks. The claim is marked **Unverified / Needs human review**. It is not declared false automatically. The writer may supply more specific evidence or revise the statement, and the reviewer makes the final decision.

**Case B: supported claim**

> Draft: "Our average score gain was 18% over 8 weeks."

In the demonstrated review, this claim produced no finding.

The distinction illustrates the design intent: identify what the available evidence establishes, what it does not establish, and what requires human attention.

---

## 8. Technical Architecture

| Layer | Technology | Responsibility |
|---|---|---|
| Frontend | React, TypeScript, Vite | Writer and reviewer interface |
| API | Python, FastAPI | Application endpoints and workflow |
| Validation | Pydantic | Request and response validation |
| Data access | SQLAlchemy | Database operations |
| Database | SQLite (current deployment); PostgreSQL supported when configured | Application records |
| Review engine | Python | Rule checks and verification |
| AI integration | Optional server-side provider | Additional review proposals |
| Document processing | python-docx | DOCX text extraction |
| Frontend hosting | Vercel | Web application deployment |
| Backend hosting | Render | API deployment |

The browser communicates with the backend over HTTPS using JSON requests and bearer-token authentication. The backend handles authentication, permissions, review processing, evidence operations and database access. Optional AI processing runs server-side, and API keys are not exposed to the frontend.

**Main backend areas:** authentication and user roles; rules and facts; draft lifecycle; review and decisions; evidence documents and proposals; source provenance; events and insights.

All endpoints are documented through OpenAPI/Swagger.

---

## 9. Testing and Verification

### Automated Tests

22 backend tests pass:

```bash
python -m pytest tests -q
```

### Evaluation

```bash
python -m evaluation.run_evaluation
```

The runner reports overall and per-rule metrics and validates results against the dataset labels.

### Production Workflow Checks

The following journeys were verified against the deployed application:

- Production sign-in and authenticated API access.
- Evidence document upload.
- Evidence proposal creation and reviewer approval.
- Fact-source provenance lookup.
- Supported numerical claim review.
- Unverified numerical claim review.
- Tone finding.
- Reviewer queue and decision workflow.

---

## 10. Local Setup

### Prerequisites

- Python 3.11 or later
- Node.js 18 or later
- Git

### Clone the Repository

```bash
git clone https://github.com/Presika-S/inkproof.git
cd inkproof
```

### Backend

```bash
cd backend
python -m venv .venv
```

Activate the virtual environment:

```bash
# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Configure environment variables using `backend/.env.example`. Set a secure `SECRET_KEY`, an appropriate `DATABASE_URL`, and the required CORS settings. Do not commit credentials or API keys.

Start the API:

```bash
uvicorn app.main:app --reload --port 8000
```

If port 8000 is in use, use port 8001 instead:

```bash
uvicorn app.main:app --reload --port 8001
```

API documentation is available at `http://127.0.0.1:8000/docs` (or port 8001 if used).

### Frontend

In a second terminal, from the repository root:

```bash
cd frontend
npm install
```

Create a local `.env` from `frontend/.env.example`:

```env
# Default backend port
VITE_API_URL=http://localhost:8000

# If the backend runs on port 8001
# VITE_API_URL=http://localhost:8001
```

Start the development server:

```bash
npm run dev
```

Create a production build:

```bash
npm run build
```

---

## 11. Demo Access

Synthetic demo accounts are available where demo seeding is enabled.

| Role | Email | Password |
|---|---|---|
| Writer | writer@demo.test | demo1234 |
| Reviewer | reviewer@demo.test | demo1234 |

These accounts are for evaluation only. Do not enter real or sensitive information.

---

## 12. Known Limitations

In the interest of accuracy, the following limitations apply to the current submission:

- **Database:** The current deployment uses SQLite on Render Free. Managed persistent database infrastructure, schema migrations, and verified automated backups and restoration remain future infrastructure milestones.
- **Evaluation data:** The 60-example dataset is synthetic. Reported metrics reflect agreement with its labels only.
- **Collaboration:** Reviewer assignment, notifications and workflow integrations are not yet implemented.
- **Evidence conflicts:** Stale-status information is available; automated conflict detection between sources is planned.

---

## 13. Product Roadmap

1. **Production-grade data durability.** Introduce managed persistent database infrastructure, schema migrations, automated backups and verified restoration, so that evidence, decisions and audit records are retained reliably.
2. **Real-world evidence intelligence.** Expand evaluation using consented organisational datasets, improve document extraction, monitor source expiry, and identify conflicting evidence. Explore advanced evidence retrieval while retaining human approval.
3. **Enterprise collaboration and quality assurance.** Introduce reviewer assignment, notifications, workflow integrations, richer permission models and broader real-world evaluation.

---

## 14. Conclusion

InkProof is not a grammar checker or a general AI writing assistant. It helps organisations determine whether the claims they publish can be justified by the rules and evidence they have approved. By combining content review, source provenance, independent verification and human decisions, it makes brand governance explainable, traceable and accountable.

---

**Team NOVARA | FutureStack Round 3**

- Live application: https://inkproof.vercel.app/
- Repository: https://github.com/Presika-S/inkproof
- API documentation: https://inkproof-api.onrender.com/docs
