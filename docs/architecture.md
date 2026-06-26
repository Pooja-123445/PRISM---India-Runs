PRISM Architecture

Overview

PRISM is a multi-signal candidate ranking engine that processes 100,000 candidate profiles and ranks them against a Senior AI Engineer job description.


System Flow

candidates.jsonl (100K)
        │
        ▼
┌─────────────────┐
│   JD Parser     │ ← jd_parser.py
│ Extracts skills │
│ YoE, locations  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Skill Extractor │ ← ranker.py: skill_hits()
│ Scans profile + │
│ career + summary│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Signal Scorer   │ ← ranker.py: score()
│ 17 dimensions   │
│ 0–110 raw pts   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Honeypot Filter │ ← built into score()
│ −20 to −50 pts  │
│ for bad profiles│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Ranked Output  │ ← rank_candidates()
│  Top 100 CSV    │
│  Scores 0.5–1.0 │
└─────────────────┘

Scoring Dimensions (17 total, max ~110 pts raw)

Dimension	Points
Job title match	20
Years of experience (5–9yr)	15
Embeddings/dense retrieval	8
Vector database	7
Retrieval/ranking systems	6
Evaluation frameworks (NDCG/MRR)	6
Product company vs. consulting	15
Preferred location	10
Platform activity	8
Recruiter response rate	6
Open-to-work flag	3
Notice period	3
GitHub activity	3
LLM/transformers	3
NLP skills	2
ML/deep learning	2
Python proficiency	3

Honeypot Detection


Duration > 600 months at one company → −50 pts

5+ expert skills with 0 duration months → −20 pts

Pure consulting firm history → −15 pts

Bad title (HR/Marketing/Content) → −30 pts


API

REST API built with FastAPI:



GET / — Health check

POST /rank — Rank all candidates

GET /candidate/{id} — Get single candidate with PRISM score


Performance


100K candidates: < 90 seconds on CPU

Peak RAM: < 4 GB

No GPU required, no external model dependencies

