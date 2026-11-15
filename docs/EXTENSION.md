# Signature Extension: X2 — Proposal Experiments (A/B Testing in GigSim)

## 1. Overview & Hypothesis
Freelancers frequently struggle between two proposal opening strategies:
- **Strategy A (Capability-Led Overview)**: Stating high-level experience, degrees, and lists of skills ("I have 6 years experience in Python and machine learning...").
- **Strategy B (Evidence-Grounded Hook)**: Opening immediately with a verified case study, specific benchmark metric lift, and a 3-step technical delivery roadmap.

**Hypothesis**: Opening immediately with verified numerical evidence (Strategy B) reduces client friction and increases client reply rates by at least 15 percentage points over traditional capability overviews.

## 2. Experimental Setup in GigSim
We deployed 200 comparable freelance proposals across 100 fixed jobs in the GigSim marketplace simulator:
- **Group A (n = 100)**: Evaluated using Strategy A.
- **Group B (n = 100)**: Evaluated using Strategy B (GigBid's default grounded writer).
- Simulated clients with hidden evaluation criteria (generic opening penalties, evidence bonuses, budget limits) rated each submission and decided whether to reply or ignore.

## 3. Results & Statistical Significance
All results are recorded in `evals/results/proposal_ab_test.json`:

| Metric | Strategy A (Capability-Led) | Strategy B (Evidence-Hook) | Absolute Lift |
| :--- | :--- | :--- | :--- |
| **Sample Size (n)** | 100 | 100 | - |
| **Replies Count** | 41 | 65 | +24 replies |
| **Reply Rate** | 41.0% | **65.0%** | **+24.0%** |
| **Average Word Count** | 185 words | 145 words | -40 words (more concise) |
| **Two-Sample Z-Score** | - | **3.41** | - |
| **Two-Tailed p-value** | - | **p = 0.00065** | **Statistically Significant (p < 0.001)** |

## 4. Conclusion
The +24.0% absolute lift is statistically significant at the 99.9% confidence level ($z = 3.41, p < 0.001$). Grounding the very first sentence in verified past metrics dramatically bypasses client skim-fatigue caused by generic AI-generated openings.
