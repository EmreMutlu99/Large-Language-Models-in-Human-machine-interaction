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
