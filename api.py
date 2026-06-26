"""
PRISM API — FastAPI server exposing ranking endpoints
Run: uvicorn api:app --reload
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import json, os
from src.ranker import score, reasoning, skill_hits
from src.jd_parser import parse_jd

app = FastAPI(title="PRISM API", version="1.0.0", description="Intelligent Candidate Ranking")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


class RankRequest(BaseModel):
    jd_text: Optional[str] = None
    top_n:   int = 100


@app.get("/")
def root():
    return {"service": "PRISM", "status": "online", "team": "Recursive Mind"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/rank")
def rank(req: RankRequest):
    """Return top_n ranked candidates for the default JD (or provided JD text)."""
    jl_path = os.getenv("CANDIDATES_JSONL", "candidates.jsonl")
    if not os.path.exists(jl_path):
        raise HTTPException(status_code=404, detail="candidates.jsonl not found")

    candidates = []
    with open(jl_path) as f:
        for line in f:
            line = line.strip()
            if line:
                candidates.append(json.loads(line))

    scored = sorted(
        ((c['candidate_id'], score(c), c) for c in candidates),
        key=lambda x: (-x[1], x[0])
    )[:req.top_n]

    hi, lo = scored[0][1], scored[-1][1]
    span   = hi - lo if hi != lo else 1

    results = []
    for i, (cid, raw, c) in enumerate(scored):
        p   = c.get('profile', {})
        sig = c.get('redrob_signals', {})
        h   = skill_hits(c)
        results.append({
            'rank':                  i + 1,
            'candidate_id':          cid,
            'score':                 round(0.5 + 0.499 * (raw - lo) / span, 4),
            'current_title':         p.get('current_title'),
            'years_of_experience':   p.get('years_of_experience'),
            'location':              p.get('location'),
            'open_to_work':          sig.get('open_to_work_flag'),
            'notice_period_days':    sig.get('notice_period_days'),
            'recruiter_response_rate': round(sig.get('recruiter_response_rate', 0), 2),
            'last_active_date':      sig.get('last_active_date'),
            'matched_skills':        [k for k, v in h.items() if v],
            'reasoning':             reasoning(c),
        })

    jd_parsed = parse_jd(req.jd_text) if req.jd_text else None

    return {
        "total_candidates_scored": len(candidates),
        "returned":                len(results),
        "jd_analysis":             jd_parsed,
        "ranked_candidates":       results,
    }


@app.get("/candidate/{candidate_id}")
def get_candidate(candidate_id: str):
    jl_path = os.getenv("CANDIDATES_JSONL", "candidates.jsonl")
    if not os.path.exists(jl_path):
        raise HTTPException(status_code=404, detail="candidates.jsonl not found")
    with open(jl_path) as f:
        for line in f:
            line = line.strip()
            if not line: continue
            c = json.loads(line)
            if c['candidate_id'] == candidate_id:
                h = skill_hits(c)
                return {
                    **c,
                    'prism_score':    round(score(c), 2),
                    'matched_skills': [k for k, v in h.items() if v],
                    'reasoning':      reasoning(c),
                }
    raise HTTPException(status_code=404, detail=f"{candidate_id} not found")
