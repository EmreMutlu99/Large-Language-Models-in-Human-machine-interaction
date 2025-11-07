# Large Language Models in Human-Machine Interaction

This repository tracks the seminar write-up on the role of LLMs in safety-critical Human-Machine Interaction (HMI). The thesis surveys how text, audio, speech-to-speech, and vision-language-action interfaces are deployed in domains such as aerospace, emergency response, and industrial operations.

## Repository Structure

```
├── paper/                   # LaTeX source of the seminar paper
│   ├── frame.tex            # Master document
│   ├── sections/            # Individual section stubs
│   └── MyBib.bib            # Bibliography entries
├── research/                # PDF corpus + tracker of reviewed papers
│   ├── *.pdf
│   └── paper_tracker.csv    # Status and notes for each reference
└── README.md
```

## Building the Paper

Use `latexmk` (TeX Live 2023+ recommended). From `paper/`:

```bash
latexmk -pdf frame.tex
```

If necessary, clean auxiliary files with `latexmk -C frame.tex`.

## Current Plan

1. Populate each section in `paper/sections/` with summaries of the selected case studies.
2. Add figures/tables (e.g., stressor vs. modality matrix) and cite papers via `MyBib.bib`.
3. Replace the placeholder abstract/keywords once the content stabilizes.

## Research Focus

- Identify how LLM-driven interfaces address situational ambiguity, time pressure, and large-scale coordination.
- Compare modalities: text planners, STT→LLM→TTS pipelines, end-to-end speech-to-speech models, and vision-language-action stacks.
- Highlight human factors (psychological impact, trust, safety guardrails) using the astronaut CUI study and related papers.

Contributions, issue reports, or paper suggestions are welcome via pull requests.
