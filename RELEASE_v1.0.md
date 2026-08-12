# Newcastle United Recruitment Analytics — v1.0 Release

## Release Status

**Status:** RELEASE READY  
**Version:** v1.0  
**Release QA:** PASSED

Newcastle Recruitment Analytics v1.0 is a decision-support framework
for succession planning and recruitment prioritisation.

The system progresses from quantitative recruitment analysis through
risk-adjusted decision modelling, scouting validation requirements,
a human-scouting decision gate, and executive reporting.

## Release Architecture

### Phase 1 — Analytical Foundation
Defines the underlying analytical framework and recruitment problem.

### Phase 2 — Recruitment Decision Model
Produces the risk-adjusted executive shortlist and decision tiers.

**Status:** FROZEN — `phase2_v1_0`

### Phase 3 — Scouting & Decision Validation
Diagnoses candidates requiring additional validation and defines
recommended scouting actions.

**Status:** FROZEN — `phase3_v1_0`

### Phase 4 — Human Scouting Decision Gate
Prevents final recruitment approval without completed human scouting
evidence.

**Status:** FROZEN — `phase4_v1_0`

### Phase 5 — Executive Reporting
Integrates recruitment rankings, risk, scouting requirements and
decision status into executive succession outputs.

**Status:** FROZEN — `phase5_v1_0`

## Executive Candidate Population

The v1.0 executive shortlist contains **9 candidates** across three
succession problems:

- Anthony Gordon — 2 candidates
- Bruno Guimaraes — 3 candidates
- Sandro Tonali — 4 candidates

## Human-Scouting Safeguard

The system deliberately separates analytical recommendation from final
recruitment approval.

A candidate cannot cross the final decision gate without completed
human scouting evidence.

At release:

- Completed human scouting records: **0**
- Final recruitment approvals: **0**
- Executive candidates awaiting scouting validation: **9**

This is the intended safe release state.

## Release QA

Whole-project release QA verifies:

- frozen Phase 2–5 structure
- required release artifacts
- row-count integrity
- player continuity across phases
- succession coverage
- decision-tier continuity
- risk-adjusted-score continuity
- scouting-action continuity
- human-scouting safeguards
- succession-ranking integrity
- README methodology and reproducibility documentation
- frozen-file write protection

**Release QA Result: PASSED**

## Key Executive Output

`frozen/phase5_v1_0/outputs/executive_master_summary_v1_0.csv`

Supporting succession briefs:

`frozen/phase5_v1_0/outputs/succession_briefs/`

## Release QA Script

`frozen/release_v1_0/scripts/release_qa_v1_0.py`

## Final Release Principle

**Analytics prioritises the decision. Human scouting validates the
decision. Neither substitutes for the other.**


