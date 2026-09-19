---
logical_name: patent_ai
google_drive_file_id: 1QmnrE_eeLQUerJJ6SNaEjw7gnQxTXbvtHrcyCmvnTrg
source_title: Patent_AI_Experiment_Dashboard_Canonical
sync_timestamp: '2026-09-19T14:18:44Z'
source_type: google_sheet
---

# Patent\_AI\_Experiment\_Dashboard\_Canonical

Export: visible worksheets only. Formula results are exported as values; dates use ISO format.
Column letters and original row numbers preserve cell positions; header rows remain in their original rows.
Visual styling, charts/images, and threaded discussions are not represented. Cell notes and merged ranges are listed where available.

## Sheet: Dashboard

Used range: `A1:H99`

Merged ranges (value remains at top-left cell): A12:H12, A13:H17, A19:H19, A1:H2, A48:H48, A72:H72, A73:H74, A86:H86, A87:H87, A96:H96, A97:H97, A98:H98, A99:H99, C25:H25, C26:H26, C27:H27, C28:H28, C29:H29, C30:H30, C31:H31, C32:H32, C33:H33, C34:H34, C35:H35, C36:H36, C37:H37, C38:H38, C39:H39, C40:H40, C41:H41, C42:H42, C43:H43, C44:H44, C45:H45, C49:H49, C50:H50, C51:H51, C52:H52, C53:H53, C54:H54, C55:H55, C56:H56, C57:H57, C58:H58, C59:H59, C60:H60, C61:H61, C62:H62, C63:H63, C64:H64, C65:H65, C66:H66, C67:H67, C68:H68, C69:H69, C75:H75, C76:H76, C77:H77, C78:H78, C79:H79, C80:H80, C81:H81, C82:H82, C83:H83

| Row | A | B | C | D | E | F | G | H |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Patent AI Experiment Dashboard |  |  |  |  |  |  |  |
| 2 |  |  |  |  |  |  |  |  |
| 3 |  |  |  |  |  |  |  |  |
| 4 | Current State | Value |  | KPI | Value |  |  |  |
| 5 | Current Benchmark | BC001-v0.1-provisional |  | Experiments logged | 18 |  |  |  |
| 6 | Current System | Retrieval baseline + candidate reranker + validated evidence assist |  | Promoted experiments | 0 |  |  |  |
| 7 | Current Champion | None yet — reranker not promoted |  | Best Recall@50 | 20% |  |  |  |
| 8 | Current Experiment | EXP-016A |  | Best Recall@100 | 40% |  |  |  |
| 9 | Benchmark Domain | Traceable biometric smart firearm |  | Best Precision@20 | 45% |  |  |  |
| 10 |  |  |  | Best median GOLD rank | 90.5 |  |  |  |
| 11 |  |  |  |  |  |  |  |  |
| 12 | Workflow |  |  |  |  |  |  |  |
| 13 | Add each run to Experiment Log → change one primary component → compare Challenger vs Champion on the same benchmark → record learning → PROMOTE / REJECT / HOLD. Never overwrite prior experiment rows or benchmark versions. |  |  |  |  |  |  |  |
| 14 |  |  |  |  |  |  |  |  |
| 15 |  |  |  |  |  |  |  |  |
| 16 |  |  |  |  |  |  |  |  |
| 17 |  |  |  |  |  |  |  |  |
| 18 |  |  |  |  |  |  |  |  |
| 19 | Current Canonical Snapshot |  |  |  |  |  |  |  |
| 20 | Experiment | Description | Results | Recall@50 | Recall@100 | Precision@20 | Median GOLD rank | Status |
| 21 | RUN-012 | 3,238-family FAMPAT rerun/export | 6/10 GOLD recovered; V0 Orbit order | 20% | 20% |  | 492 | BASELINE |
| 22 | EXP-013 | Blind title/abstract reranking | Done | 20% | 40% | 45% | 90.5 | HOLD / INCONCLUSIVE |
| 23 | EXP-011 | Evidence-assisted full-text review | 5-patent sample: ~30 min → 10–15 min |  |  |  |  | PARTIALLY\_VALIDATED |
| 24 |  |  |  |  |  |  |  |  |
| 25 | EXP-013 completed adjudication | Value | Scope / limitation |  |  |  |  |  |
| 26 | Newly adjudicated publications | 18.0 | Completed analyst decisions; two existing GOLD records are separate |  |  |  |  |  |
| 27 | Include Yes | 7.0 | Newly adjudicated publications |  |  |  |  |  |
| 28 | Include No | 11.0 | Newly adjudicated publications |  |  |  |  |  |
| 29 | Publication inclusion yield | 38.88888889% | 7/18 among newly adjudicated publications |  |  |  |  |  |
| 30 | New analyst report groups | 15.0 | Three pairs grouped for client-report purposes; Questel IDs retained |  |  |  |  |  |
| 31 | Includable new candidate groups | 5.0 | Candidate groups; not established net-new relevant families |  |  |  |  |  |
| 32 | Excluded new candidate groups | 10.0 | Analyst report-family grouping |  |  |  |  |  |
| 33 | New-candidate family yield | 33.33333333% | 5/15 analyst-defined groups |  |  |  |  |  |
| 34 | Top-20 publications evaluated | 20.0 | 18 completed decisions plus two existing GOLD positives |  |  |  |  |  |
| 35 | Top-20 positive publications | 9.0 | Includes the two existing GOLD records |  |  |  |  |  |
| 36 | Publication Precision@20 | 45% | 9/20 original ranked records; not Questel-family precision |  |  |  |  |  |
| 37 | Top-20 analyst report groups | 17.0 | No source rows or Questel identifiers merged |  |  |  |  |  |
| 38 | Includable top-20 groups | 7.0 | Analyst report-family grouping |  |  |  |  |  |
| 39 | Excluded top-20 groups | 10.0 | Analyst report-family grouping |  |  |  |  |  |
| 40 | Report-inclusion yield@20 | 41.17647059% | 7/17 family-deduplicated analyst report groups |  |  |  |  |  |
| 41 | Net-new relevant-family yield | N/A | Complete historical-report comparison pending |  |  |  |  |  |
| 42 | Analyst review minutes | N/A | Until supplied |  |  |  |  |  |
| 43 | PA-001 status | COMPLETED | KZ6216U decision is abstract-only; not a claim of full-text availability |  |  |  |  |  |
| 44 | Reconstructed mapping | Ambiguity retained | Ranks 6/7 remain unordered; same L/No decisions; no metric effect |  |  |  |  |  |
| 45 | EXP-013 decision | HOLD / INCONCLUSIVE | V0 top 20 lacks equivalent adjudication; no promotion |  |  |  |  |  |
| 46 |  |  |  |  |  |  |  |  |
| 47 |  |  |  |  |  |  |  |  |
| 48 | EXP-014 — Orbit versus frozen AI top-20 comparison |  |  |  |  |  |  |  |
| 49 | Status | AWAITING\_ADJUDICATION | Setup only; no final evaluation decision |  |  |  |  |  |
| 50 | Baseline | RUN-012 Orbit ordering | Same frozen 3,238-family export |  |  |  |  |  |
| 51 | Challenger | rs\_v0.2\_blind\_ta\_rerank | Frozen EXP-013 ranking |  |  |  |  |  |
| 52 | Component evaluated | Relevance Scorer | Ranking evaluation; no model or system change |  |  |  |  |  |
| 53 | Single primary change | ordering method | Disclosure, benchmark, universe, query/database, relevance standard, ground truth, rankings and family policy fixed |  |  |  |  |  |
| 54 | Hypothesis | At least 2 more includable groups | V1 finds at least two more includable unique report-family groups in the first 20 publication slots and passes both recall guardrails |  |  |  |  |  |
| 55 | Resolved publications | 2.0 | Existing decisions: WO2021194584A2 family H/Yes; CN207144670U L/No |  |  |  |  |  |
| 56 | Unresolved publications | 18.0 | Shuffled analyst packet; no inferred labels |  |  |  |  |  |
| 57 | Top-20 publication overlap | 1.0 | CN207144670U; Questel FAN overlap also one |  |  |  |  |  |
| 58 | Known report groups | 2.0 | One includable, one excluded; unresolved families remain unassigned |  |  |  |  |  |
| 59 | Primary metric: V0 includable groups | N/A | Number of analyst-includable unique report-family groups in first 20 publication slots |  |  |  |  |  |
| 60 | V0 publication Precision@20 | N/A | Pending complete adjudication |  |  |  |  |  |
| 61 | V0 report-family inclusion yield | N/A | Pending complete adjudication and group reconciliation |  |  |  |  |  |
| 62 | Analyst review minutes | N/A | One total active time requested; access delays excluded |  |  |  |  |  |
| 63 | Recall@50 guardrail | Pass (frozen metrics) | V1 2/10 &gt;= V0 2/10; no new run |  |  |  |  |  |
| 64 | Recall@100 guardrail | Pass (frozen metrics) | V1 4/10 &gt; V0 2/10; no new run |  |  |  |  |  |
| 65 | Final EXP-014 decision | N/A | No PROMOTE / REJECT / HOLD outcome calculated |  |  |  |  |  |
| 66 | Pre-registered PROMOTE | V1 at least 2 groups better | Requires both recall guardrails to pass |  |  |  |  |  |
| 67 | Pre-registered REJECT | V1 fewer groups OR guardrail failure | Guardrail failure takes precedence over group-count HOLD condition |  |  |  |  |  |
| 68 | Pre-registered HOLD | Equal or 1 group better | With both recall guardrails passing |  |  |  |  |  |
| 69 | Final V0 report-group denominator | N/A | Two groups currently identifiable; do not assume all other records are separate families |  |  |  |  |  |
| 70 |  |  |  |  |  |  |  |  |
| 71 |  |  |  |  |  |  |  |  |
| 72 | EXP-015 — retrieval volume preflight |  |  |  |  |  |  |  |
| 73 | HOLD — DESIGN REVISION REQUIRED AFTER VOLUME PREFLIGHT |  |  |  |  |  |  |  |
| 74 |  |  |  |  |  |  |  |  |
| 75 | EXP015-015A-Q1 | 23935.0 | FAMPAT families; executed 2026-09-17; export blocked by volume. |  |  |  |  |  |
| 76 | EXP015-015A-Q2 | 493993.0 | FAMPAT families; executed 2026-09-17; export blocked by volume. |  |  |  |  |  |
| 77 | Fields / filters | TI/AB/CLMS | FAMPAT; Title, Abstract and Claims only; no other filters. |  |  |  |  |  |
| 78 | Other queries | Paused | 015A-Q3/Q4, 015B-Q1 and 015C-Q1–Q4 paused; baseline 00-Q1 not rerun. |  |  |  |  |  |
| 79 | Final metrics | N/A | Union, GOLD recovery, incremental GOLD / candidate families, marginal GOLD per 1,000: N/A. |  |  |  |  |  |
| 80 | Evidence | Analyst report | Screenshots reported outside repository; not supplied to Codex. |  |  |  |  |  |
| 81 | Decision | HOLD | Query-design volume failure. No component promoted or rejected as a whole. |  |  |  |  |  |
| 82 | Pending action | Design revision | Predeclare volume checks; control high-collision terms and functional relationships. |  |  |  |  |  |
| 83 | Source | EXP-015 record | experiments/BC001/EXP-015/preflight/volume-preflight-evidence.md |  |  |  |  |  |
| 84 |  |  |  |  |  |  |  |  |
| 85 |  |  |  |  |  |  |  |  |
| 86 | EXP-016A — feature-aware title/abstract ranking |  |  |  |  |  |  |  |
| 87 | REJECT — Recall@20 fell below its guardrail; median retrieved-GOLD rank worsened by more than 10%. |  |  |  |  |  |  |  |
| 88 |  |  |  |  |  |  |  |  |
| 89 | Metric | EXP-013 |  | EXP-016A | Change |  |  |  |
| 90 | Recall@20 | 20% |  | 10% | -10 |  |  |  |
| 91 | Recall@50 | 20% |  | 20% | 0 |  |  |  |
| 92 | Recall@100 | 40% |  | 30% | -10 |  |  |  |
| 93 | Recall@200 | 50% |  | 30% | -20 |  |  |  |
| 94 | Median GOLD rank | 90.5 |  | 142.5 | 52 |  |  |  |
| 95 |  |  |  |  |  |  |  |  |
| 96 | Recall denominator: GOLD-10. Median: six retrieved GOLD families. All 3,238 records ranked exactly once. |  |  |  |  |  |  |  |
| 97 | Ranking frozen before private evaluation. Original key unavailable; all six reconstructed GOLD mappings are exact. |  |  |  |  |  |  |  |
| 98 | Deterministic rule extraction; evidence judgments are not analyst labels. Component remains a challenger. |  |  |  |  |  |  |  |
| 99 | Source: experiments/BC001/EXP-016A/evaluation/evaluation.md |  |  |  |  |  |  |  |

### Export warnings

- Merged cell spans are described rather than visually reproduced.

## Sheet: Experiment Log

Used range: `A1:V19`

Structured rows (wide, long-text, or sparse tab). Unlisted cells are blank; no populated columns are omitted.

### Row 1

- **A1**: Experiment ID
- **B1**: Date
- **C1**: Benchmark ID
- **D1**: Benchmark Version
- **E1**: Base System
- **F1**: Challenger System
- **G1**: Hypothesis / Objective
- **H1**: Primary Component Changed
- **I1**: From Version
- **J1**: To Version
- **K1**: What Changed
- **L1**: Recall@50
- **M1**: Recall@100
- **N1**: Precision@20
- **O1**: Gold in Top 10
- **P1**: Median Rank of Retrieved GOLD
- **Q1**: Analyst Minutes
- **R1**: Model Cost USD
- **S1**: Guardrail / Side Effect
- **T1**: Learning
- **U1**: Decision
- **V1**: Notes

### Row 2

- **A2**: HIST-000
- **B2**: 2026-09-12T00:00:00
- **C2**: BC001
- **D2**: 0.1-provisional
- **G2**: Original analyst patentability search
- **H2**: Human baseline
- **K2**: ~12–15 queries across tools; ~2,000–3,000 patents/families reviewed
- **Q2**: ~5 days
- **S2**: Not a single-query retrieval baseline
- **T2**: Expert process baseline; query construction + review were bottlenecks
- **U2**: BASELINE
- **V2**: Historical human-process baseline

### Row 3

- **A3**: EXP-001
- **B3**: 2026-09-12T00:00:00
- **C3**: BC001
- **D3**: 0.1-provisional
- **G3**: Test LLM disclosure decomposition
- **H3**: Feature Extractor
- **I3**: raw
- **J3**: fe\_v0.2\_bc001\_corrected
- **K3**: Claude E1–E16 + analyst corrections
- **S3**: One hallucinated feature; exact F1–F8 not separately signed off
- **T3**: Useful decomposition after corrections; no time-saving proof
- **U3**: DIAGNOSTIC
- **V3**: Partially validated

### Row 4

- **A4**: EXP-002
- **B4**: 2026-09-12T00:00:00
- **C4**: BC001
- **D4**: 0.1-provisional
- **G4**: Test clarification-question generation
- **H4**: Feature Extractor
- **K4**: Five inventor questions generated
- **S4**: Questions were unnecessary/non-blocking
- **T4**: Generic ambiguity generation added avoidable effort
- **U4**: REJECT
- **V4**: Rejected

### Row 5

- **A5**: EXP-003
- **B5**: 2026-09-12T00:00:00
- **C5**: BC001
- **D5**: 0.1-provisional
- **G5**: Capture analyst SOP and Orbit grammar
- **H5**: Search Controller
- **J5**: sc\_v0.0\_analyst\_sop\_spec
- **K5**: Broad→narrow workflow; result bands; syntax/operator examples
- **S5**: Requirements captured, not implemented
- **T5**: Query planning is iterative control, not one Boolean string
- **U5**: DIAGNOSTIC
- **V5**: Requirements artifact

### Row 6

- **A6**: EXP-004
- **B6**: 2026-09-12T00:00:00
- **C6**: BC001
- **D6**: 0.1-provisional
- **G6**: Test 15-query staged portfolio
- **H6**: Query Planner
- **J6**: qp\_v0.1\_ladder\_rejected
- **K6**: Claude CB1–CB9 + 15-query ladder
- **S6**: Unsupported syntax; proximity too wide; overused AND
- **T6**: Syntactic plausibility ≠ usable Orbit query
- **U6**: REJECT
- **V6**: Rejected

### Row 7

- **A7**: EXP-005
- **B7**: 2026-09-12T00:00:00
- **C7**: BC001
- **D7**: 0.1-provisional
- **G7**: Formulate focused Query B
- **H7**: Query Planner
- **I7**: qp\_v0.1\_ladder\_rejected
- **J7**: qp\_v0.2\_query\_b\_baseline
- **K7**: Claude proposed 10D auth/control query
- **S7**: Analyst rated weak; needed substantial repair
- **T7**: Main failure: breadth/morphology/Orbit expression
- **U7**: REJECT
- **V7**: Still source of first AI retrieval run

### Row 8

- **A8**: RUN-005A
- **B8**: 2026-09-12T00:00:00
- **C8**: BC001
- **D8**: 0.1-provisional
- **G8**: Execute initial Query B snapshot
- **H8**: Retrieval Adapter
- **K8**: 3,091-family FAMPAT run; described as 10D
- **S8**: No ordered export preserved
- **T8**: Recovered 5/10 GOLD; historical diagnostic only
- **U8**: SUPERSEDED
- **V8**: Keep separate from 3,238 rerun

### Row 9

- **A9**: RUN-006
- **B9**: 2026-09-13T00:00:00
- **C9**: BC001
- **D9**: 0.1-provisional
- **G9**: Execute human Query A comparator
- **H9**: Retrieval Adapter
- **K9**: 799 FAMPAT results; human-built query
- **S9**: Field provenance inconsistent
- **T9**: Recovered 6/10 GOLD
- **U9**: BASELINE
- **V9**: Comparator only

### Row 10

- **A10**: EXP-007
- **B10**: 2026-09-13T00:00:00
- **C10**: BC001
- **D10**: 0.1-provisional
- **G10**: Compare Query A vs B overlap/recovery
- **H10**: Evaluation
- **K10**: A∩B=142; A∪B=3,748
- **S10**: Applies only to original snapshots
- **T10**: Union recovered 7/10 GOLD
- **U10**: DIAGNOSTIC
- **V10**: Do not mix with 3,238 rerun

### Row 11

- **A11**: EXP-008
- **B11**: 2026-09-13T00:00:00
- **C11**: BC001
- **D11**: 0.1-provisional
- **G11**: Test seed-patent-grounded terminology
- **H11**: Terminology Engine
- **I11**: generic
- **J11**: te\_v0.3\_seed\_grounded\_candidate
- **K11**: Extracted P1–P12 terms from seed patents
- **S11**: No controlled retrieval run
- **T11**: Analyst preferred seed-patent terms over web/generic
- **U11**: DIAGNOSTIC
- **V11**: Best-supported terminology method; retrieval-unvalidated

### Row 12

- **A12**: EXP-009
- **B12**: 2026-09-13T00:00:00
- **C12**: BC001
- **D12**: 0.1-provisional
- **G12**: Test web-grounded terminology
- **H12**: Terminology Engine
- **I12**: generic
- **J12**: te\_v0.2\_web
- **K12**: Web-derived W1–W12 terms
- **S12**: Several noisy/secondary terms
- **T12**: Useful first-pass vocabulary, insufficient alone
- **U12**: DIAGNOSTIC
- **V12**: Not promoted

### Row 13

- **A13**: EXP-010
- **B13**: 2026-09-13T00:00:00
- **C13**: BC001
- **D13**: 0.1-provisional
- **G13**: Convert web terms into 5-query portfolio
- **H13**: Query Planner
- **K13**: Five Orbit-ready queries proposed
- **S13**: Q1/Q2 major rebuild; syntax/proximity issues
- **T13**: More terms did not solve planning/syntax
- **U13**: REJECT
- **V13**: Rejected

### Row 14

- **A14**: EXP-011
- **B14**: 2026-09-15T00:00:00
- **C14**: BC001
- **D14**: 0.1-provisional
- **G14**: Test evidence-assisted review on 20 analyst-selected patents
- **H14**: Evidence Extractor
- **J14**: ee\_v0.1\_fulltext\_passage\_assist
- **K14**: Full-text feature mapping + evidence citations
- **Q14**: 10–15
- **S14**: Only 5 patents analyst-validated
- **T14**: 5/5 cited passages accepted; review time ~30 min → 10–15 min
- **U14**: PARTIALLY\_VALIDATED
- **V14**: Most validated AI capability so far

### Row 15

- **A15**: RUN-012
- **B15**: 2026-09-16T00:00:00
- **C15**: BC001
- **D15**: 0.1-provisional
- **G15**: Create complete ordered reranking benchmark
- **H15**: Retrieval Adapter
- **J15**: retrieval\_v0.1\_fampat\_20260916\_and\_variant
- **K15**: 3,238-family FAMPAT export; AND variant
- **L15**: 20%
- **M15**: 20%
- **P15**: 492.0
- **S15**: 4 GOLD absent; differs from initial 10D snapshot
- **T15**: Full-set GOLD recovery 6/10
- **U15**: BASELINE
- **V15**: Current V0 retrieval baseline

### Row 16

- **A16**: EXP-013
- **B16**: 2026-09-16T00:00:00
- **C16**: BC001
- **D16**: 0.1-provisional
- **E16**: RUN-012
- **F16**: rs\_v0.2\_blind\_ta\_rerank
- **G16**: Test blind title/abstract reranking
- **H16**: Relevance Scorer
- **I16**: Orbit order
- **J16**: rs\_v0.2\_blind\_ta\_rerank
- **K16**: Blind rerank of all 3,238 families
- **L16**: 20%
- **M16**: 40%
- **N16**: 45%
- **P16**: 90.5
- **Q16**: N/A
- **S16**: V0 top 20 not equivalently adjudicated; three analyst report-family pairs have different Questel FAN IDs; theft-triggered locking schema review pending
- **T16**: Recall@100 2/10→4/10; median retrieved-GOLD rank 492→90.5
- **U16**: HOLD
- **V16**: PA-001 COMPLETED. HOLD / INCONCLUSIVE: V0 top 20 lacks equivalent adjudication. Newly adjudicated: 18 (7 Yes, 11 No), inclusion 7/18 = 38.9%. Publication Precision@20 incl. 2 GOLD: 9/20 = 45%. New analyst report groups: 15 (5 included, 10 excluded), yield 5/15 = 33.3%. Top-20 analyst report groups: 17 (7 included, 10 excluded), report-inclusion yield 7/17 = 41.2%. Net-new relevant-family yield and analyst minutes: N/A. Reconstructed mapping; unordered ranks 6/7 L/No ambiguity has no metric effect. No promotion.

### Row 17

- **A17**: EXP-014
- **B17**: 2026-09-16T00:00:00
- **C17**: BC001
- **D17**: 0.1-provisional
- **E17**: RUN-012 Orbit ordering of the 3,238-family export
- **F17**: rs\_v0.2\_blind\_ta\_rerank
- **G17**: V1 finds at least two more analyst-includable unique report-family groups in the first 20 publication slots than V0 while passing both recall guardrails
- **H17**: Relevance Scorer
- **I17**: RUN-012 Orbit ordering
- **J17**: rs\_v0.2\_blind\_ta\_rerank (frozen EXP-013)
- **K17**: ordering method; ranking evaluation; no model or system change
- **L17**: N/A
- **M17**: N/A
- **N17**: N/A
- **O17**: N/A
- **P17**: N/A
- **Q17**: N/A
- **R17**: N/A
- **S17**: V1 Recall@50 &gt;= V0 Recall@50; V1 Recall@100 &gt; V0 Recall@100. All rankings, universe, ground truth and family policy fixed.
- **T17**: N/A pending adjudication
- **U17**: AWAITING\_ADJUDICATION
- **V17**: PROMOTE if V1 has &gt;=2 more includable unique report-family groups and both recall guardrails pass; REJECT if V1 has fewer or violates either guardrail; HOLD if equal or one better (guardrails pass). 2 resolved, 18 unresolved; overlap 1; final metrics and review minutes N/A. No decision calculated.

### Row 18

- **A18**: EXP-015
- **B18**: 2026-09-17T00:00:00
- **C18**: BC001
- **D18**: 0.1-provisional
- **E18**: RUN-012 and intended same-session baseline
- **F18**: Controlled 2x2 structure / vocabulary
- **G18**: Record original feature-specific retrieval volume preflight
- **H18**: Query Planner / Search Controller
- **I18**: Current monolithic structure + current vocabulary
- **J18**: Original EXP-015 2x2 design
- **K18**: Analyst executed EXP015-015A-Q1/Q2; neither exported
- **L18**: N/A
- **M18**: N/A
- **N18**: N/A
- **O18**: N/A
- **P18**: N/A
- **Q18**: N/A
- **R18**: N/A
- **S18**: FAMPAT; TI/AB/CLMS; family-level; unchanged benchmark; no additional filters
- **T18**: Q1 23,935 families; Q2 493,993 families. Broad document-level AND failed operational volume preflight.
- **U18**: HOLD — DESIGN REVISION REQUIRED AFTER VOLUME PREFLIGHT
- **V18**: Remaining queries paused; baseline not rerun. All final metrics N/A. No component promotion or wholesale rejection. Screenshots external; not supplied.

### Row 19

- **A19**: EXP-016A
- **B19**: 2026-09-17T00:00:00
- **C19**: BC001
- **D19**: 0.1-provisional
- **E19**: EXP-013 on RUN-012
- **F19**: rs\_v0.3\_feature\_aware\_ta
- **G19**: Feature-aware title/abstract reranking of the fixed 3238-family universe
- **H19**: Relevance Scorer
- **I19**: rs\_v0.2\_blind\_ta\_rerank
- **J19**: rs\_v0.3\_feature\_aware\_ta
- **K19**: Deterministic feature/relationship extraction and approved scoring formula
- **L19**: 20%
- **M19**: 30%
- **N19**: N/A
- **O19**: N/A
- **P19**: 142.5
- **Q19**: N/A
- **R19**: N/A
- **S19**: Recall@20 1/10 fails 2/10 guardrail; Recall@200 3/10; median worsens &gt;10%
- **T19**: Determinism did not improve retrieval ordering of known GOLD; rule extraction needs separate evaluation
- **U19**: REJECT
- **V19**: Frozen before private evaluation. Six GOLD mappings exact in reconstructed key. Challenger only; CURRENT\_SYSTEM unchanged.

## Sheet: Benchmark Inputs

Used range: `A1:G19`

| Row | A | B | C | D | E | F | G |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Category | Input / Artifact | Version / Set | Status | Value / Count | Frozen? | Notes |
| 2 | Case | Benchmark | BC001-v0.1-provisional | PROVISIONAL | SmartGun | Yes for current experiments | F1–F8 remains AI-normalized/partially validated |
| 3 | Features | Feature schema | F1–F8 v0.1 provisional | PARTIAL / APPROXIMATE | 8.0 | Yes for current experiments | Underlying concepts reviewed; exact F-number schema not line-by-line signed off |
| 4 | Ground Truth | Known-good set | GOLD-10 | CONFIRMED | 10.0 | Yes | Known-good set, not exhaustive universe |
| 5 | Ground Truth | Additional judged set | ADDITIONAL-JUDGED-5 | PARTIAL | 5.0 | Yes | Replaces incorrect LOW-5 label |
| 6 | Ground Truth | Hard negatives | NEG-5 | CONFIRMED membership | 5.0 | Yes | Formal later per-item N not frozen for all |
| 7 | Historical Retrieval | Initial Query B snapshot | RUN-005A | CONFIRMED count / partial exact execution | 3091.0 | Yes | 10D described; no ordered export preserved |
| 8 | Historical Retrieval | Human Query A | RUN-006 | CONFIRMED count | 799.0 | Yes | 6/10 GOLD; field provenance inconsistent |
| 9 | Historical Evaluation | A+B union | EXP-007 | CONFIRMED original snapshots | 3748.0 | Yes | 7/10 GOLD; do not mix with RUN-012 |
| 10 | Current Retrieval Baseline | Query B-like AND variant | RUN-012 | CONFIRMED | 3238.0 | Yes | 2026-09-16 complete export; 6/10 GOLD |
| 11 | Current V0 Metric | Recall@50 | RUN-012 | CONFIRMED | 2/10 | Yes | 20% |
| 12 | Current V0 Metric | Recall@100 | RUN-012 | CONFIRMED | 2/10 | Yes | 20% |
| 13 | Current V1 Metric | Recall@50 | EXP-013 | CONFIRMED | 2/10 | Yes | 20% |
| 14 | Current V1 Metric | Recall@100 | EXP-013 | CONFIRMED | 4/10 | Yes | 40% |
| 15 | Current V1 Metric | Median rank of retrieved GOLD | EXP-013 | CONFIRMED | 90.5 | Yes | Improved from 492 |
| 16 | Pending Validation | V1 top-20 adjudication | PA-001 | COMPLETED | 20.0 | No | PA-001 completed: 18 analyst decisions + 2 GOLD. V0 comparative adjudication and net-new report comparison remain outstanding. |
| 17 | Historical Effort | Analyst search/review/report | HIST-000 | CONFIRMED approx. | ~5 days | Yes | ~4 search/review + ~1 report |
| 18 | Historical Effort | Patents/families reviewed | HIST-000 | APPROXIMATE | ~2,000–3,000 | Yes | Analyst estimate |
| 19 | Historical Effort | Historical query count | HIST-000 | APPROXIMATE | ~12–15 | Yes | Across multiple tools/methods |

## Sheet: Component Versions

Used range: `A1:G9`

| Row | A | B | C | D | E | F | G |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Component | Current Proposed Version | Validation Status | Purpose | Source Experiment | Champion? | Known Limitations |
| 2 | Feature Extractor | fe\_v0.2\_bc001\_corrected | Partially validated | Disclosure → structured feature state | EXP-001 | No | One hallucinated feature removed; exact F1–F8 schema not independently signed off; no cross-case test |
| 3 | Terminology Engine | te\_v0.3\_seed\_grounded\_candidate | Analyst-preferred; retrieval-unvalidated | Ground search vocabulary in patent language | EXP-008 | No | No controlled Orbit run measured impact; depends on relevant seed access |
| 4 | Query Planner | qp\_v0.2\_query\_b\_baseline | Executed but analyst-rated weak | Generate Orbit search strategy/queries | EXP-005 / RUN-005A | No | Incomplete synonyms, syntax repair, noise control issues; 3,091 vs 3,238 provenance mismatch |
| 5 | Retrieval | retrieval\_v0.1\_fampat\_20260916\_and\_variant | Fully executed and frozen | Retrieve candidate families from FAMPAT | RUN-012 | No | Single query; 6/10 GOLD; 4 GOLD absent; live database changes |
| 6 | Relevance Scorer | rs\_v0.2\_blind\_ta\_rerank | HOLD / INCONCLUSIVE | Rank retrieved families | EXP-013 | No | V1 top 20 adjudicated; V0 comparison pending; three report-family groups differ from Questel IDs; model/version and label calibration limitations remain |
| 7 | Evidence Extractor | ee\_v0.1\_fulltext\_passage\_assist | Partially validated on 5 patents | Support analyst review with passages/reasoning | EXP-011 | No | Small validation sample; inference needs explicit paragraph/reasoning |
| 8 | Search Controller | sc\_v0.0\_analyst\_sop\_spec | Requirements only; not implemented | Broaden/narrow/seed/stop decision logic | EXP-003 | No | No autonomous loop validated |
| 9 | Relevance Scorer (challenger) | rs\_v0.3\_feature\_aware\_ta | REJECT; challenger only | Feature-aware title/abstract ranking | EXP-016A | No | Recall@20 1/10; median GOLD rank 142.5. Rule-based extraction; no promotion. |

## Sheet: Metric Definitions

Used range: `A1:E9`

| Row | A | B | C | D | E |
| --- | --- | --- | --- | --- | --- |
| 1 | Metric | Definition | Why it matters | Valid when | Canonical status |
| 2 | Full-set GOLD recovery | GOLD-10 families present anywhere in retrieved set / 10 | Separates retrieval coverage from ranking quality | Frozen result universe + family mapping | RUN-012 = 6/10 |
| 3 | Recall@50 | GOLD-10 families in first 50 / 10 | Measures analyst review budget of 50 | Ordered candidate list exists | V0 2/10; V1 2/10 |
| 4 | Recall@100 | GOLD-10 families in first 100 / 10 | Measures review budget of 100 | Ordered candidate list exists | V0 2/10; V1 4/10 |
| 5 | Publication Precision@20 | Analyst-positive publications among original V1 top 20 / 20; includes two existing GOLD positives | Measures practical usefulness of top results | All top-20 outcomes evaluated; identical-content ambiguity must not affect outcomes | EXP-013: 9/20 = 45%; PA-001 COMPLETED; HOLD pending V0 comparison |
| 6 | Median rank of retrieved GOLD | Median rank among GOLD families actually present in retrieval set | Shows ranking compression for known-good art | Same retrieval universe for V0/V1 | 492 → 90.5 |
| 7 | Net-new relevant-family yield | Relevant V1 top families not already in historical known/report set | Tests discovery value beyond GOLD-10 | Top candidates analyst-adjudicated | PENDING |
| 8 | Evidence-review time | Analyst time to review AI evidence vs manual baseline | Measures human-effort reduction | Same review task and sample | ~30 min → 10–15 min on 5-patent sample |
| 9 | Family-deduplicated report-inclusion yield@20 | Includable analyst-defined report groups among top-20 records / all analyst-defined report groups | Separates client-report grouping from publication precision | Explicit analyst grouping; Questel IDs retained | EXP-013: 7/17 = 41.2%; not a Questel-family precision estimate |
