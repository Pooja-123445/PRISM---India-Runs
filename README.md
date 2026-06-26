# PRISM 🔍
**Predictive Ranking & Intelligent Signal Matching**

> India Runs Data & AI Challenge — Track 1: Data Challenge  
> Team: **Recursive Mind** | Pooja M. · Malathy S.

---

## What PRISM Does

PRISM ranks 100,000 candidates against a Senior AI Engineer JD using a multi-signal scoring engine that goes beyond keyword matching.

```
JD Text ──► JD Parser ──► Signal Weights
Candidates.jsonl ──► Skill Extractor ──► Multi-Signal Scorer ──► Ranked Top 100
                                          ▲
                              Behavioral Signals (redrob)
```

## Scoring Architecture

| Dimension | Max Points | Rationale |
|---|---|---|
| Job Title Match | 20 | Semantic role fit |
| Years of Experience | 15 | JD target: 5–9 yrs |
| Embeddings / Dense Retrieval | 8 | Core JD requirement |
| Vector Database (Pinecone/Qdrant/FAISS) | 7 | Core JD requirement |
| Ranking / Retrieval Systems | 6 | Core JD requirement |
| Evaluation Frameworks (NDCG/MRR) | 6 | Explicitly required |
| LLM / Transformers | 3 | Bonus |
| NLP Skills | 2 | Bonus |
| ML / Deep Learning | 2 | Bonus |
| Python Proficiency | 3 | Baseline requirement |
| Product vs. Consulting History | 15 | Signal quality |
| Preferred Location | 10 | Pune/Noida/Hyderabad/NCR |
| Platform Activity (last active) | 8 | Engagement signal |
| Recruiter Response Rate | 6 | Hire-ability signal |
| Open-to-Work Flag | 3 | Availability |
| Notice Period | 3 | Speed-to-join |
| GitHub Activity | 3 | Code craft signal |
| Honeypot Detection | −20 to −50 | Data integrity guard |

## Quick Start

```bash
git clone https://github.com/DataDynamoQueen/PRISM
cd PRISM
pip install -r requirements.txt

# Rank candidates
python src/ranker.py candidates.jsonl submission.csv

# Validate submission
python validate_submission.py submission.csv

# Start API server
uvicorn api:app --reload
```

## Project Structure

```
PRISM/
├── src/
│   ├── ranker.py        # Core scoring engine
│   └── jd_parser.py     # Job description parser
├── api.py               # FastAPI REST API
├── requirements.txt
├── submission.csv        # Final ranked output (top 100)
└── docs/
    └── architecture.md
```

## Results

- **100,000** candidates processed in < 90 seconds
- **Top candidate**: NLP Engineer, 6.5yr, Pune — hits all core JD signals
- **Title distribution of top 100**: ML Engineer (14%), AI Engineer (10%), Search Engineer (7%), NLP Engineer (6%)
- Passes official `validate_submission.py` with "Submission is valid ✅"

## Anti-Gaming Measures

- Consulting firm penalty (TCS/Infosys/Wipro/Accenture = −15)
- Honeypot detection: >600 month tenure = −50; 5+ expert skills with 0 duration = −20
- Scores checked to be monotonically non-increasing
- Candidate IDs checked for uniqueness and CAND_XXXXXXX format

## Team

| Name | Role |
|---|---|
| Pooja M. | Lead — scoring engine, API, dashboard |
| Malathy S. | Data analysis, validation, documentation |

Mentor: Narendran M., CSE Dept., Sona College of Technology
