# t3lab-claude-skills

A library of **Claude Skills** for the ACE/AEC industry — coordination, clash
detection, Revit, PDF markup comparison, comment aggregation, and issue/RFI
management — plus a **security vetting layer** that audits community-contributed
skills against malware and prompt-injection.

Packaged as a Claude Code **plugin marketplace**: 5 plugins (one per domain)
that bundle these Claude Skills.

## What's inside
```
skills/            5 software groups · 39 skills (see docs/skill-taxonomy.md)
plugins/           5 marketplace plugins bundling a curated subset of the skills
scripts/           validate_skill.py · audit_skill.py · build_taxonomy.py · validate_marketplace.py
.claude/agents/    skill-auditor — security-review agent for skills
.github/           CI (skill-validation), CODEOWNERS, PR template
docs/              skill-taxonomy.md, roadmap.md, security-model.md
templates/         SKILL_TEMPLATE.md
tests/fixtures/    malicious-skill — a hostile sample used to test the auditor
```

## Five software groups
Skills are grouped **by software** (`skills/<software>/`) and tagged with
**metadata** (`software`, `discipline`, `category`) so they can be
cross-referenced by *discipline* and by *category*.

| Group | Software | Skills |
|-------|----------|--------|
| `revit` (20) | Revit / Dynamo / pyRevit | `rv-shared-parameters`, `rv-schedule-qa`, `rv-warnings-audit`, `rv-model-audit`, `rv-family-naming`, `rv-model-compare`, `rv-script-helper`, `rv-batch-export`, `rv-sheet-naming`, `rv-shared-coordinates`, `rv-comment-locations`, `rv-cad-import`, `rv-image-drafting`, `rv-create-sheets`, `rv-spellcheck-review`, `rv-create-family`, `rv-family-image`, `rvstr-beam-cad`, `rvstr-column-tools`, `rvmep-duct-velocity` |
| `navisworks` (2) | Navisworks | `clash-report-analysis`, `model-federation` |
| `acc-bim360` (2) | Autodesk Construction Cloud / BIM 360 | `acc-issue-register`, `coordination-issue-log` |
| `bluebeam-pdf` (2) | Bluebeam / PDF | `pdf-markup-compare`, `comment-aggregation` |
| `office-data` (13) | Excel / CSV (software-agnostic) | `rfi-tracker`, `risk-register`, `action-item-tracker`, `change-order-log`, `weekly-report`, `submittal-log`, `drawing-register-qa`, `iso19650-naming-check`, `iso19650-project-audit`, `cobie-validation`, `spellcheck-review`, `boq-compare`, `quantity-takeoff` |

> **Revit skills are named by discipline** — `rv-` (general / multi-discipline),
> `rvarc-` (Architecture), `rvstr-` (Structural), `rvmep-` (MEP) — in the form
> `<prefix>-<a>-<b>` (exactly two segments), enforced by `validate_skill.py`.
> Rules: [`CONTRIBUTING.md`](CONTRIBUTING.md).

**Three lookup tables** (by software / discipline / category) are generated
automatically: [`docs/skill-taxonomy.md`](docs/skill-taxonomy.md). Roadmap:
[`docs/roadmap.md`](docs/roadmap.md).

## Install (Claude Code plugin)
Add the marketplace once, then install the plugins you need:
```
/plugin marketplace add thanhtranarch/t3lab-claude.skills-revit
/plugin install revit-authoring@t3lab-ace-skills
/plugin install standards-qa@t3lab-ace-skills
/reload-plugins
```
Or just ask Claude in chat: *"Add the t3lab-ace-skills marketplace and install
the revit-authoring plugin."* Once installed, Claude selects skills automatically
from their `description`; invoke one by hand with `/<plugin>:<skill>`
(e.g. `/revit-authoring:rv-schedule-qa`).

To try or develop locally without installing:
`claude --plugin-dir ./plugins/revit-authoring`.

## Quick start (run the scripts directly)
Many skills ship with scripts that run immediately on the bundled sample data:
```bash
pip install -r requirements.txt

# Example: analyze a Navisworks clash report
python skills/navisworks/clash-report-analysis/scripts/parse_clash.py \
       skills/navisworks/clash-report-analysis/assets/sample_clash.xml

# Compare markups between two PDF revisions
python skills/bluebeam-pdf/pdf-markup-compare/scripts/compare_markup.py \
       skills/bluebeam-pdf/pdf-markup-compare/assets/rev_a.pdf \
       skills/bluebeam-pdf/pdf-markup-compare/assets/rev_b.pdf

# Track RFIs: aging, overdue, ball-in-court
python skills/office-data/rfi-tracker/scripts/track_rfis.py \
       skills/office-data/rfi-tracker/assets/sample_rfis.csv --as-of 2026-07-24

# Compare two Revit model versions (added / deleted / changed)
python skills/revit/rv-model-compare/scripts/compare_models.py \
       skills/revit/rv-model-compare/assets/sample_model_v1.csv \
       skills/revit/rv-model-compare/assets/sample_model_v2.csv
```

## Security (the highlight)
Because the repo accepts skills from many contributors, every skill is vetted in
several layers before merge — see [`docs/security-model.md`](docs/security-model.md):

1. `scripts/validate_skill.py` — SKILL.md structure & metadata.
2. `scripts/audit_skill.py` — static scan for malware / dangerous commands /
   data exfiltration / prompt-injection (regex + AST, stdlib + pyyaml only).
3. `@skill-auditor` agent — context-aware review with a PASS/FAIL verdict.
4. CI `.github/workflows/skill-validation.yml` — runs layers 1–2 on every PR.
5. `CODEOWNERS` — final maintainer sign-off.

```bash
# Validate the manifest + every skill:
python scripts/validate_marketplace.py
python scripts/validate_skill.py plugins
python scripts/audit_skill.py    plugins

# Prove the auditor catches malware:
python scripts/audit_skill.py tests/fixtures/malicious-skill   # exit != 0
```

## Contributing
See [`CONTRIBUTING.md`](CONTRIBUTING.md). In short: copy
`templates/SKILL_TEMPLATE.md`, write your skill, run validate + audit, and open a
PR (CI + review will vet it).

## Requirements
Python 3.11+. Install dependencies with `pip install -r requirements.txt`. The
vetting layer needs only `pyyaml` plus the standard library.

## License
Released under the **MIT License** — see [`LICENSE`](LICENSE). You are free to
use, modify, and share it; keep the copyright and license notice.
