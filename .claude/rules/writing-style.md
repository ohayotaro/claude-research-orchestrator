# Writing style (papers and research notes)

All paper drafts and `docs/research/*` notes are written in English.

## Structure: IMRaD

- **Introduction** — context, gap, contribution claims, paper structure.
- **Related work** — survey, positioning. May come before or after methods depending on venue.
- **Methods** — what you did, in enough detail to reproduce. Cite tools and datasets.
- **Results** — what you found. Numbers, figures, tables. No interpretation here.
- **Discussion** — interpretation, implications, limitations, future work.
- **Conclusion** — short summary of contribution and impact.

## Voice and tense

- Active voice by default. "We trained the model on ..." not "The model was trained on ...".
- Past tense for what you did. Present tense for what is true / what figures show.

## Hedging

- Hedge claims to match evidence, but do not over-hedge.
- "Our results suggest X" is fine when the effect is real but not definitive.
- Avoid stacked hedges: not "may potentially possibly indicate".

## Precision

- Quantify whenever possible. "30% improvement (95% CI [25, 35])" beats "much better".
- Define every acronym on first use.
- Use the same name for the same thing throughout. Pick a term in the introduction and stick with it.

## Figures and tables

- Every figure and table is numbered and referenced in the text.
- Captions are self-contained: a reader looking only at figures should grasp the result.
- Axes labeled with units. Error bars defined in the caption (SD, SE, 95% CI?).

## Citations

- See `citation-rigor.md`. Every non-original claim cites a source.

## Length discipline

- Default to brevity. If a sentence does not change the reader's understanding, cut it.
- No "In this paper, we will discuss ..." filler. Start with substance.

## Forbidden phrases

- "It is well known that" — cite it instead.
- "Recent advances" — be specific about which advances.
- "Our novel approach" — let the reader judge novelty.
