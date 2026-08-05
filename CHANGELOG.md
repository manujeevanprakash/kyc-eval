# Changelog

## baseline-error-analysis — 2026-08-05

State of the prototype at the point error analysis began.
Six cases pass on risk signal. The failures are in the summaries.

### Removed
- `risk_score`. Computed and stored, never read by any decision.
- `compute_completeness` and the 0.70 threshold. Encoded document
  presence as a weighted decimal with unjustified 70/30 weights.

### Changed
- Deferral now comes from agent findings and names the missing
  documents instead of reporting a percentage.
- Sanctions evaluated before the deferral check. The old order
  returned CANNOT_CLASSIFY for a sanctioned client with thin
  documents, asking them for more paperwork.
- `SANCTIONS_MATCH_DETECTED` split into `SANCTIONS_POTENTIAL_MATCH`
  and `SANCTIONS_MATCH_CONFIRMED`. Registry now carries identifiers.
- Regulatory basis keyed by finding, not by agent. Deterministic
  agents cite PCMLTFA or FINTRAC. Only the Case Summary agent
  cites OSFI E-23.
- Case summary audit record stores the full verified and
  needs_review lists rather than counts, and records the model.
- Model: `groq/llama-3.1-8b-instant` to `groq/openai/gpt-oss-120b`.

### Added
- `date_of_birth` on all clients.
- KYC-005, sanctions candidate match.
- KYC-006, confirmed sanctions match. One field of difference
  from KYC-005, opposite outcome.

### Known failures, not yet fixed
- KYC-006 summary downgrades a confirmed hard stop and instructs
  the officer to obtain documents from the client.
- KYC-004 summary names the wrong missing document. The risk
  engine drops the specific gap.
- KYC-003 truncates mid-sentence.