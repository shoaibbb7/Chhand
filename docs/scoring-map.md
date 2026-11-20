# Chhand — Evaluation & Judging Scoring Map

This document connects judging criteria directly to concrete code implementations, linguistic modules, and automated test cases within the repository.

| Judging Criterion | Key Architectural Innovation | Repository Implementation Evidence | Automated Verification Tests |
|---|---|---|---|
| **1. Innovation** | **Linguistic Guardrail Architecture**: Breaks the reliance on LLMs for prosodic counting. Implements authentic Indic Pingala Chhand Shastra in deterministic Python, treating LLMs strictly as creative proposers and never as self-verifying judges. | • `app/meter/devanagari.py`<br>• `app/meter/syllables.py`<br>• `app/meter/weights.py`<br>• `app/meter/scanner.py` | • `tests/test_devanagari.py`<br>• `tests/test_syllables.py`<br>• `tests/test_weights.py`<br>• `tests/test_scanner.py` |
| **2. AI Depth** | **Generate-and-Verify Loop with Automatic Retries**: The LLM generates candidate lines conditioned on meter diagnosis and rhyme constraints; every candidate is executed through the deterministic scanner. Zero unverified candidates reach the UI. | • `app/llm/client.py`<br>• `app/llm/prompts.py`<br>• `app/llm/verify_loop.py` | • `tests/test_verify_loop.py` (`test_valid_candidate_accepted`, `test_invalid_candidate_strictly_rejected`, `test_retry_cap_respected`) |
| **3. Verifiable Prototype** | **Full-Stack Working Studio**: Minimalist, distraction-free Devanagari scansion workspace featuring under-syllable laghu (`•`) and guru (`—`) scansion marks, hairline design, live error highlights, and instant accept/skip actions. | • `public/index.html`<br>• `public/styles.css`<br>• `public/js/app.js`<br>• `public/js/editor.js`<br>• `public/js/meterBar.js`<br>• `public/js/suggestions.js` | • Live local testing on `http://127.0.0.1:8000`<br>• `tests/test_api.py` (`test_analyze_endpoint_valid_doha`, `test_analyze_endpoint_broken_line`) |
| **4. Technical Implementation** | **Unicode-Exact Grapheme Cluster Tracking**: NFC normalization maintaining a 1:1 character index map back to original source spans for pixel-perfect highlighting. Fully offline fallback; zero runtime crashes without API key. | • `app/meter/normalize.py`<br>• `app/meter/templates.py`<br>• `app/errors.py`<br>• `scripts/check_meter.py` | • `tests/test_devanagari.py::test_unicode_normalization_and_mapping`<br>• `tests/test_api.py::test_rewrite_endpoint_when_llm_unconfigured` |
| **5. Human Control** | **Poet-in-the-Loop Interaction**: Suggestions are presented as optional cards with transparent syllable counts and meaning notes. Poet explicitly chooses to `Accept` (updating line) or `Skip` (preserving original line). Supports custom meter patterns. | • `public/js/suggestions.js`<br>• `public/js/editor.js`<br>• `app/meter/templates.py` (custom patterns) | • `tests/test_templates.py::test_custom_valid_pattern`<br>• `tests/test_templates.py::test_custom_invalid_pattern` |

---

## Verified Golden Examples in Test Suite

1. **Doha Baseline** (13 \| 11):
   - Line 1: `मन का दीपक जब जले` (13 matras) \| `मिटे अँधेरा दूर` (11 matras)
   - Line 2 (Fixed): `सीख सदा सच की रखो` (13 matras) \| `साथ रहेगा नूर` (11 matras)
2. **Doha Broken Line** (13 \| 13):
   - Line 2 (Broken): `सीख सदा सच की रखो` (13) \| `साथ रहेगा फिर नूर` (13 - Over by 2, overflow starts at 'नूर')
3. **Chaupai Baseline** (16 \| 16 \| 16 \| 16):
   - `जय हनुमान ज्ञान गुन सागर` (16)
   - `जय कपीस तिहुँ लोक उजागर` (16)
   - `राम दूत अतुलित बल धामा` (16)
   - `अंजनि पुत्र पवनसुत नामा` (16)
