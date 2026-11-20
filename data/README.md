# Chhand Data Reference & Provenance

This directory contains curated datasets for meter testing, benchmark validation, and phonetic rhyming.

## Datasets Overview

1. `sample_dohas.json`: Curated collection of 15 classical Doha verses from public-domain literature (Kabir Das, Abdur Rahim Khan-i-Khana, Tulsidas) and reviewed baseline couplets.
2. `sample_chaupais.json`: Reviewed 16-matra Awadhi Chaupais from public-domain traditional sources (Tulsidas's *Ramcharitmanas* and *Hanuman Chalisa*).
3. `broken_examples.json`: Controlled test cases derived by introducing exact prosodic errors (extra words, dropped words, foreign characters) to verify the deterministic scanner and diagnostic engine.
4. `rhyme_words.txt`: Grouped Devanagari dictionary of authentic Hindi poetic words organized by phonetic ending sound (तुक / rhyme tail).

## Public Domain & Ethical Licensing
- All classical couplets are in the public domain, originating from 15th–17th century Bhakti and Riti era manuscripts.
- The sample couplet used in the UI mockup (`मन का दीपक जब जले | मिटे अँधेरा दूर` / `सीख सदा सच की रखो | साथ रहेगा फिर नूर`) was composed directly for Chhand's instructional suite.
- No copyrighted contemporary song lyrics or commercial lyrics are included.

## Validation Status Taxonomy
- `reviewed`: Every charan was verified manually against Pingala Chhand Shastra rules and confirmed by the automated test suite.
- `needs_review`: Historic folk, Awadhi, or Braj Bhasha verses featuring dialectal poetic license (e.g. vowel shortening or archaic nasalization) flagged for future dialect-specific tuning.
