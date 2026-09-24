# Item schema (one JSON object per item, a JSON array per domain file)

{
  "id": "<domain>-NN",
  "domain": "code" | "math" | "summary",
  "task": "The full question/request the answers respond to. For summary items this includes the source passage.",
  "clean": "A correct, competent answer.",
  "subtle": "The clean answer with ONE minimal defect that makes it wrong.",
  "subtle_defect": "Ground truth: exactly what is wrong in `subtle` and why.",
  "subtle_defect_type": "short tag, e.g. off-by-one, sign-flip, swapped-attribution",
  "obvious": "The clean answer with ONE blatant defect a skim reader would catch.",
  "obvious_defect": "Ground truth for `obvious`.",
  "padded": "The clean answer, still fully correct, made ~60-100% longer with filler that adds no information.",
  "verify": "domain-specific verification artefact (see agent brief)"
}

Rules that apply to every domain:
- `subtle` must differ from `clean` by the smallest possible edit (ideally one token, one number, one line). Same length, same style, same formatting. No comments, hedges or wording that hints at the defect.
- The defect in `subtle` must make the answer actually wrong, and a careful reader must be able to prove it using ONLY the information in `task` plus basic arithmetic / language semantics. No external or world knowledge required.
- `obvious` must also be a minimal-ish edit but blatant (e.g. final answer contradicts own working, function returns a constant, summary states the opposite of the headline finding).
- `padded` must contain no new facts, claims or code behaviour. Filler = restating the question, throat-clearing, redundant recap, generic best-practice remarks. It must not introduce any error.
- Everything is original writing. For summary sources use fictional organisations, places and people so world knowledge can neither help nor hurt.
- Vary the defect types across items; do not reuse the same trick more than twice per domain.
