# Chhand Couplets Dataset & Training Foundation

This directory houses the dataset schema and preliminary labeled data for future fine-tuning and domain adaptation.

## Dataset Specification

Each JSONL record represents an annotated couplet or stanza with prosodic metadata:

```json
{
  "text": "मन का दीपक जब जले | मिटे अँधेरा दूर\nसीख सदा सच की रखो | साथ रहेगा नूर",
  "language": "hi",
  "meter": "doha",
  "charan_pattern": [13, 11, 13, 11],
  "author": "Chhand Benchmark",
  "source": "Instructional Corpus",
  "validation_status": "reviewed"
}
```

## Annotation Procedure & Human Review
1. **Public Domain Ingestion**: Historical works by Kabir, Rahim, and Tulsidas are extracted from open historical archives.
2. **Text Normalization**: Unicode NFC normalization, standardized danda punctuation, and nukta preservation.
3. **Double Blind Prosodic Review**: Computational scansion by the Python meter engine followed by manual human verification by an Indic computational linguist.
4. **License Verification**: Ensuring zero copyrighted contemporary lyrics are admitted.

## Prompt Adaptation vs. Model Fine-Tuning
- **Prompt Adaptation (Current MVP)**: In-context few-shot prompting with strict engine verification. The LLM acts as an unconstrained linguistic generator; correctness is enforced entirely downstream by the deterministic engine.
- **Model Fine-Tuning (Finale Roadmap)**: Supervised LoRA fine-tuning on metered Devanagari verse. A fine-tuned model internalizes syllable counts and Pingala structures directly into its weights, dramatically increasing candidate acceptance rates on the first pass (reducing verification loop retries).
