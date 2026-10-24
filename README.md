# InkProof — Brand Governance with Verifiable Evidence

**Team NOVARA | FutureStack — Round 2: The Build**

**Live Application:** https://inkproof.vercel.app/  
**API Documentation:** https://inkproof-api.onrender.com/docs  
**Source Code:** https://github.com/Presika-S/inkproof

## 1. About InkProof

InkProof is a web application that helps teams review draft communications against approved brand rules and facts. It identifies potentially problematic claims, displays supporting evidence, and provides a structured workflow for human review and approval.

Instead of treating every automated flag as a final verdict, InkProof distinguishes verified findings from suggestions that require further review. This helps writers and reviewers make more transparent, evidence-based decisions.

## 2. Problem We Solve

Teams publishing under a brand need to keep claims, figures, terminology, and tone consistent. Traditional manual reviews can be slow, outdated facts can remain in drafts, and automated tools may flag content without clearly explaining why.

InkProof addresses these challenges by connecting review findings to rules, facts, quoted text, and verification checks while keeping final decisions in human hands.

## 3. Features Implemented in Round 2

### Authentication and roles
- User registration and sign-in.
- Password hashing and signed authentication tokens.
- Writer and reviewer permissions.

### Rules and facts library
- Retrieve approved rules and facts.
- Update fact values and validity dates through the API.
- Track fact versions and identify drafts that may need rechecking after a fact changes.

### Evidence-based review
- Detect selected hype terms, ranking claims, and numerical mismatches.
- Connect findings to relevant rules, facts, and text quotations.
- Independently check whether the rule is approved, the quote appears in the draft, the fact is current and approved, and relevant keywords appear in the draft.

### Optional AI-assisted review
- Generate additional review proposals when server-side AI configuration is available.
- Recheck proposals before presenting them as verified findings.
- Continue with rule-based review when the AI key is unavailable.

### DOCX import
- Upload Word documents for text extraction.
- Supports a configured file-size limit of 5 MB.

### Draft and reviewer workflow
- Create, list, and manage drafts through API endpoints.
- Record decisions to uphold or waive individual findings, with written reasons for waivers.
- Finalize reviews by approving a draft or requesting changes.

### Intent Lock and insights
- Provide frontend warnings when edits may alter important claims, figures, or calls to action.
- Record acceptance and dispute events through API endpoints.
- Display basic rule-health and fact-change information.

**Feature status:** Core backend tests and the frontend production build have passed. Some browser workflows and production behaviours still require further verification; these are identified in the project report rather than presented as completed testing.

## 4. How InkProof Works

1. **Sign in:** The writer or reviewer accesses the application.
2. **Access the library:** The application retrieves relevant rules and facts.
3. **Prepare a draft:** The writer enters text or selects a DOCX file.
4. **Run a review:** The rule engine identifies potential issues; optional AI can suggest additional findings.
5. **Inspect evidence:** The user examines the quoted passage, rule, fact, and verification result.
6. **Submit the draft:** The draft is sent to the review workflow.
7. **Make decisions:** The reviewer upholds or waives findings and records reasons where required.
8. **Finalize:** The reviewer approves the draft or requests changes.
9. **Review history:** Drafts, events, and available insights support follow-up.

## 5. Technology Stack

| Component | Technology | Purpose |
|---|---|---|
| Frontend | React 18, TypeScript, Vite | Interactive web application |
| Backend | Python, FastAPI, Pydantic | API endpoints and request validation |
| Data access | SQLAlchemy | Database interaction |
| Database | SQLite in the current configuration; PostgreSQL support when configured | Store application data |
| Review engine | Python | Rule checks and independent verification |
| AI integration | Anthropic API, optional | Additional review proposals |
| Document processing | python-docx | Extract text from DOCX files |
| Frontend hosting | Vercel | Deploy the web application |
| Backend hosting | Render | Host the API |

## 6. Architecture and Security

The browser communicates with the FastAPI backend over HTTP(S) using JSON requests and authentication tokens. The backend handles permissions, validation, review logic, and database operations.

The optional AI provider is accessed from the backend, not directly from the browser. The AI key must remain server-side. When AI review is enabled, draft text and relevant rule and fact information are sent to the configured provider.

Passwords are hashed, tokens are signed using a server-side secret, and reviewer-only operations enforce role permissions. Demo accounts and sample content are intended for testing.

InkProof is a prototype: rate limiting, password reset, and email verification are not implemented. Production data persistence and security under real-world workloads still need further validation.

## 7. Testing and Reliability

The project report records the following checks:

- **Backend:** Six automated tests passed.
- **Frontend:** Type-check and production build passed.
- **Local API:** A smoke test covering sign-in, review, and CORS preflight passed.
- **Deployment:** The frontend and API documentation were reachable during the team's checks.

The full live workflow, real-key AI review, browser-based DOCX import, and persistence across redeployments were not yet verified in the report. No accuracy or load-testing results are claimed.

## 8. Current Limitations

InkProof is a working prototype, not a finished enterprise platform.

- Claim detection focuses on selected English-language patterns, including percentages, star ratings, rankings, and keywords.
- The verifier checks evidence presence, approval, freshness, and keyword matching; it does not prove every claim is true in every sense.
- The seeded rules and facts library is small and synthetic.
- Creating rules and facts through the interface, PDF import, image checks, a draft comparison viewer, charts, and in-place draft editing are not built.
- Live AI behaviour, complete end-to-end review, and production data persistence require further testing.

These limitations guide the next development phase and help keep the project's claims accurate.

## 9. Planned Improvements for Round 3

### 1. Persistent data and stronger governance
Introduce managed PostgreSQL, schema migrations, tested backups and restoration, finer-grained permissions, and an append-only decision history that records who made each decision and when.

### 2. Evidence-source ingestion
Allow teams to upload and version source documents, link facts to their sources, detect expired or conflicting evidence, and require human approval of extracted facts.

### 3. Measurable review quality and collaboration
Build a labelled evaluation dataset, measure precision and recall for each rule, add regression tests, and introduce reviewer assignments, notifications, and selected workflow integrations.

These are planned improvements, not features already delivered.

## 10. Running the Project Locally

### Prerequisites
- Python 3.11 or later
- Node.js 18 or later
- Git

### Backend

From the repository root:

```bash
cd backend
python -m venv .venv
```

Activate the environment on Windows:

```powershell
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Copy `.env.example` to `.env`, configure the required values, and start the API:

```bash
uvicorn app.main:app --reload --port 8000
```

Run the backend tests:

```bash
pytest
```

### Frontend

Open a second terminal from the repository root:

```bash
cd frontend
npm install
```

Create a local `.env` file based on `.env.example` and set:

```dotenv
VITE_API_URL=http://localhost:8000
```

Start the frontend:

```bash
npm run dev
```

Build the production frontend:

```bash
npm run build
```

For local development, configure the backend environment variables using `backend/.env.example`. Never commit real secrets or API keys to the repository.

## 11. Demo Accounts

When `SEED_DEMO=true` is configured, the application can seed synthetic demo data and the following accounts, as described in the project README:

- **Writer:** `writer@demo.test`
- **Reviewer:** `reviewer@demo.test`
- **Demo password:** `demo1234`

Use these accounts only if they are enabled in the deployed environment. Do not use demo credentials for sensitive or real user information.

## 12. Conclusion

InkProof connects brand rules, factual references, automated checks, and human decisions in a single review workflow. Round 2 establishes the deployed frontend, backend API, core review logic, and reviewer decision capabilities.

Round 3 will focus on persistent data, traceable evidence sources, and measurable review quality. The long-term goal is to make brand review more transparent, accountable, and reliable without treating AI output as unquestionable evidence.

---

**Project Links**

- Live application: https://inkproof.vercel.app/
- API documentation: https://inkproof-api.onrender.com/docs
- Public source repository: https://github.com/Presika-S/inkproof

*Team NOVARA | FutureStack Round 2 — The Build*
