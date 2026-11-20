Chhand
A meter-aware writing assistant for Hindi poetry.

Chhand helps writers work with traditional Hindi matra-based forms. It checks each section of a poem against a selected meter, explains count differences, suggests alternative wording, and provides Hindi rhyme suggestions.

The current MVP focuses on Hindi written in Devanagari and on three writing workflows: Poems, Meters, and Rhymes.

Project status: MVP. This README describes the functionality included in the current MVP only. It does not present planned finale work as completed functionality.

The problem
Writing within a traditional meter involves more than choosing words that sound appropriate. Each section must follow a matra pattern, and the writer may need to inspect syllable weight and pronunciation to understand why a line does not fit.

This checking is often done manually. It interrupts the writing process and makes it harder for a writer to experiment with alternative phrasing.

Chhand brings meter checking and writing assistance into one workspace.

What Chhand does
The MVP provides three connected areas:

Poems
The Poems editor is the main writing workspace. A writer can:

Enter a poem section by section in Devanagari.
Select Doha, Chaupai, or a custom matra pattern.
See the calculated and required matra counts for each section.
Review matched, over-count, under-count, incomplete, or uncertain results where applicable.
Inspect matra and syllable details, including cumulative counts and highlighted positions.
Request alternative wording for a line that does not fit the selected target.
Accept or reject each suggested rewrite individually.
Use rhyme suggestions while working on a poem.
Accepting a suggestion updates the selected section and triggers a fresh analysis. Rejecting a suggestion leaves the original text unchanged.

Meters
The Meters page explains the supported patterns and lets writers choose a structure before writing.

The current built-in patterns are:

Meter	Charan pattern	Structure
Doha	13 / 11 / 13 / 11	Four charans with alternating targets
Chaupai	16 / 16 / 16 / 16	Four charans with equal targets
Custom	User-defined	Positive integer target for each charan
The Custom Meter Builder allows a writer to define a pattern and use it in the Poems editor.

The matra pattern is the scope of the current automated check. Traditional conventions beyond the implemented checks should not be assumed to have been validated.

Rhymes
The Rhymes page provides Hindi rhyme discovery using the project's word list and rhyme-matching logic.

A writer can:

Search for rhymes using a Hindi word or line ending.
View exact and approximate matches separately when returned by the matcher.
Explore the available rhyme-ending groups.
Copy a result or move it into the poem-writing workflow.
Rhyme quality depends on pronunciation and context. The feature is intended as a writing aid, not as a complete validator for Urdu ghazal conventions or every form of Hindi rhyme.

How the analysis works
Meter analysis is performed by the Python engine. It is not delegated to the language model.

At a high level, the engine:

Normalizes the submitted Devanagari text while retaining source-position information.
Identifies relevant characters and forms syllable or akshara units.
Assigns laghu and guru weights according to the implemented Hindi matra rules.
Calculates the cumulative matra count for the line.
Compares the result with the selected charan target.
Returns a status, count difference, diagnostic information, and source positions for the interface.
Pronunciation can affect a scan. Schwa handling and other context-dependent readings are treated according to the engine's implemented rules and available overrides. An uncertain reading should be reviewed rather than treated as an unquestionable result.

AI-assisted rewriting
The rewrite feature uses a generate-and-verify workflow:

The application sends the original line, target, and analysis context to the configured language model.
The model proposes candidate rewrites.
Each candidate is scanned independently by the deterministic meter engine.
Candidates that fail the configured target are discarded.
Only candidates that pass the meter check are presented as meter-verified suggestions.
The writer decides whether to accept or reject a suggestion.
The meter engine verifies the implemented matra-count requirement. It does not mathematically prove that a rewrite preserves every nuance of the original meaning; meaning preservation remains a generation objective for the language model and a judgement for the writer.

Technology
Part	Technology	Responsibility
Frontend	HTML, CSS, vanilla JavaScript	Poems, Meters, and Rhymes interfaces
Backend	Python, FastAPI	HTTP API and application orchestration
Validation	Pydantic	Request and response models
Meter analysis	Python modules in app/meter/	Devanagari processing, weighting, scanning, and diagnosis
AI requests	Google GenAI SDK (google-genai)	Asynchronous requests via Gemini Interactions API
Configuration	python-dotenv	Local environment configuration
Tests	pytest	Unit and API tests
Code quality	Ruff	Linting and formatting checks
Deployment	Vercel	Static frontend and Python API deployment configuration
The frontend is served as static files; it does not require a separate JavaScript build step.

Architecture

The meter engine and rhyme matcher can perform their core work without an LLM API key. The LLM is used for rewrite generation, not for deciding whether a line passes the meter check.

Repository layout
chhand/
├── app/
│   ├── api/             # FastAPI route handlers
│   ├── llm/             # Provider client, prompts, and verification loop
│   ├── meter/           # Devanagari processing and meter engine
│   ├── rhyme/           # Rhyme-tail extraction and suggestions
│   ├── config.py        # Environment-based settings
│   ├── schemas.py       # Pydantic models
│   └── main.py          # FastAPI application
├── public/
│   ├── index.html
│   ├── styles.css
│   └── js/              # Frontend modules
├── data/
│   ├── sample_dohas.json
│   ├── sample_chaupais.json
│   ├── broken_examples.json
│   └── rhyme_words.txt
├── tests/               # Meter, verification, and API tests
├── scripts/             # Local development and meter CLI utilities
├── training/            # MVP dataset notes and starter labelled data
├── docs/                # Architecture and supporting documentation
├── requirements.txt
├── requirements-dev.txt
├── pyproject.toml
└── vercel.json
The training/ directory is a preparation resource only. A fine-tuned model is not part of the current MVP runtime.

Data included
The current project dataset contains:

17 Doha examples.
6 Chaupai examples.
10 deliberately broken examples used for checking meter failures and diagnostics.
A starter Hindi rhyme word list grouped by ending.
Dataset entries should retain their source references, pronunciation notes, expected pattern, and validation status. Examples that have not been reviewed should not be presented as verified test fixtures.

The examples support development and testing; they are not a claim that the engine handles every dialect, pronunciation, or traditional prosodic convention.

Running locally
Requirements
Python 3.11 or newer
pip
An API key for the configured language-model provider if you want to use AI rewriting
Meter analysis and dictionary-based rhyme lookup do not require an LLM API key.

1. Clone the repository
git clone <YOUR_PUBLIC_REPOSITORY_URL>
cd chhand
Replace the placeholder with the repository's public Git URL.

2. Create and activate a virtual environment
Windows PowerShell

py -m venv .venv
.venv\Scripts\Activate.ps1
macOS / Linux

python3 -m venv .venv
source .venv/bin/activate
3. Install dependencies
For application use:

pip install -r requirements.txt
For development and tests:

pip install -r requirements-dev.txt
4. Configure environment variables
Copy .env.example to .env and fill in the provider settings when AI rewriting is required.

GEMINI_API_KEY=
GEMINI_MODEL=gemini-3.8-flash
GEMINI_TIMEOUT_SECONDS=30
GEMINI_MAX_CANDIDATES=4
MAX_RETRIES=3
Keep .env private. Do not commit API keys or place them in frontend JavaScript.

5. Start the application
uvicorn app.main:app --reload
Open the local URL shown by Uvicorn, normally:

http://127.0.0.1:8000
The API health endpoint is available at:

http://127.0.0.1:8000/api/health
FastAPI's interactive API documentation is normally available at /docs during local development.

API overview
The MVP exposes the following application endpoints:

Method	Endpoint	Purpose
GET	/api/health	Application and service health information
POST	/api/analyze	Analyze poem charans against a selected meter
POST	/api/rewrite	Generate and verify alternative wording for a line
POST	/api/rhyme	Find Hindi rhyme suggestions
GET	/api/rhyme/families	Return available rhyme-ending groups
For the exact request and response fields, use the Pydantic schemas in app/schemas.py and the API documentation served by the running application. The API implementation is the source of truth if this summary and the code differ.

Tests and code checks
Run the automated tests with:

python -m pytest -q
Run Ruff lint checks with:

ruff check .
Check formatting with:

ruff format --check .
The test suite covers Devanagari classification, syllable processing, weights, meter templates, scanning, rewrite verification, and API behavior. LLM-dependent tests should use mocked provider responses so that the suite does not require a live API key.

A successful test run demonstrates that the implementation satisfies its test cases. It does not, by itself, establish complete coverage of Hindi pronunciation or poetic tradition.

Deployment
The repository includes Vercel configuration for the static frontend and FastAPI serverless entry point.

Before deploying:

Push the repository to the intended public Git host.
Import the repository into Vercel.
Configure the required server-side environment variables in the Vercel project settings.
Deploy the application.
Open the deployed site and test the health, analysis, rhyme, and rewrite workflows.
Confirm that rewrite requests work with the configured provider and that scanning remains available if the provider is unavailable.
Do not publish a deployment URL in this README until it has been deployed and tested. Add the verified URL near the top of this file when available.

Current scope and limitations
The current MVP focuses on Hindi Devanagari, Doha, Chaupai, custom matra patterns, Hindi rhyme suggestions, and AI-assisted rewriting with deterministic matra verification.

The following are not included in this MVP:

Urdu script and Arooz analysis.
Bengali script and Bengali meter analysis.
Text-to-speech recitation or synchronized audio highlighting.
Lyric-sheet export.
A deployed fine-tuned or adapted model.
Full validation of every traditional rule, dialect, or pronunciation variant.
These capabilities should not be described as available until they are implemented and tested.

Design principle
Chhand is intended to assist the writer, not replace the writer's judgement. The application identifies meter issues and offers alternatives, while the writer remains responsible for the poem and decides which suggestions to keep.

The engine checks the meter. The writer makes the poem.

License
This project is distributed under the MIT License. See LICENSE for details.
