# Shortlist Golden Set v1.2 — Self-contained packet

This packet contains 12 unique frozen shortlist cases plus a stored JD/source file for every case.

## Source quality

- Exact frozen historical sources: Microsoft 200015839, Microsoft 200054592, Microsoft 200051931 (user-supplied exact evaluated JD), Microsoft 200055557, R37/R1 RCM, COUNT, Cisco 2024434, Cisco 2024101.
- Official same-job-ID recoveries: Flexport 8158027, Flexport 8110066, Amazon 10499366. These preserve the exact employer job IDs and official posting bodies recovered after the original evaluation, but are not byte-for-byte historical local snapshots.
- Partial frozen historical source: Cisco 2023232. Its decision/mapping/gap dimensions are valid; strict Role Understanding completeness remains provisional.

## Eval policy

11 cases are eligible for all five semantic dimensions. Cisco 2023232 should mark `role_understanding_completeness` as PROVISIONAL / SKIPPED_FOR_STRICT_JD_FIDELITY while scoring the other four dimensions normally.

The evaluator must never fetch a live posting when a source in this packet is available.
