# GigBid Data Card

## 1. Dataset Summary & Lineage
GigBid employs a combined real-world and statistically grounded synthetic dataset compliant with the instructor's specifications for the AI-4016 R&D Assignment.

### Primary Datasets Cited & Integrated:
1. **Upwork Job Postings Dataset 2024 (50k records)**
   - Author: Asaniczka (Kaggle)
   - License: Open Data Commons Open Database License (ODbL)
   - Role in GigBid: Provides real distribution of job titles, client budgets, country origins, hourly vs fixed rates, and job descriptions used in `data/pricing_history_1500.json`.
2. **Freelance Contracts Dataset (1.3M entries)**
   - Author: Asaniczka (Kaggle)
   - License: ODbL
   - Role in GigBid: Informs hourly rates ($35 to $95/hr) and contract completion duration distributions.
3. **Freelancer Success, Earnings, and Churn Prediction**
   - Author: Sarvesh Chhetri (Kaggle)
   - License: CC BY-SA 4.0
   - Role in GigBid: Calibrates baseline win rates, response times, and review score thresholds.

## 2. Synthetic Generation & Ground Truth Augmentation
Where real-world platform data is private or unlabelled, realistic synthetic generation was used (as explicitly permitted by the TA) to construct:
- **3 Comprehensive Freelancer Persona Corpora**:
  - `sample-ai-engineer` (Alex Morgan): CV, 20 detailed case studies, 15 verified reviews, 150 past proposals (30% won, 30% replied, 40% ignored).
  - `sample-web-dev` (Priya Patel): CV, 20 full-stack web & SaaS case studies, 150 proposals.
  - `sample-data-analyst` (Marcus Vance): CV, 20 data engineering & BI case studies, 150 proposals.
- **200 Dev Evaluation Jobs (`evals/datasets/dev_eval_jobs_200.json`)**:
  - 180 persona-aligned jobs with ground-truth `bid_or_skip` labels and fair price bands.
  - 10 Prohibited Scam Jobs (free work requests, Telegram/WhatsApp contacts, crypto deposits).
  - 10 Planted Adversarial Prompt-Injections (system role overrides, HTML comments, instruction leakage).

## 3. Preprocessing & Ethical Safeguards
- **PII Scrubbing**: Real email addresses and phone numbers in raw job descriptions are scrubbed using regex masking (`[REDACTED_CONTACT_INFO]`).
- **Platform Respect**: No web scraping or unofficial Upwork page parsers were used. All data ingestion is file-based or served via official MCP API contracts.
- **Limitations**: Synthetic proposals simulate realistic freelancer responses but cannot fully replicate long-term client conversational nuance across multiple weeks.
