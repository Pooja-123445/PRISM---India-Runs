"""
PRISM - Predictive Ranking & Intelligent Signal Matching
Core ranking engine for India Runs Data & AI Challenge
Team: Recursive Mind | Pooja M. & Malathy S.
"""

import json
import csv
from datetime import datetime, date
from pathlib import Path

TODAY = date(2026, 6, 25)

CORE_SKILLS = {
    'embeddings': ['embedding', 'embeddings', 'sentence-transformer', 'sentence transformer',
                   'openai embeddings', 'bge', 'e5', 'dense retrieval', 'bi-encoder'],
    'vector_db':  ['pinecone', 'weaviate', 'qdrant', 'milvus', 'faiss', 'opensearch',
                   'elasticsearch', 'vector database', 'vector db', 'vector search', 'ann', 'hnsw'],
    'retrieval':  ['retrieval', 'rag', 'hybrid search', 'semantic search', 'bm25',
                   'information retrieval', 'reranking', 're-ranking', 'search ranking'],
    'python':     ['python'],
    'eval':       ['ndcg', 'mrr', 'map@', 'mean average precision', 'precision@',
                   'a/b test', 'ab test', 'evaluation framework', 'offline eval', 'auc-roc'],
    'llm':        ['llm', 'large language model', 'gpt', 'bert', 'transformer',
                   'fine-tun', 'lora', 'qlora', 'peft', 'huggingface', 'hugging face'],
    'nlp':        ['nlp', 'natural language', 'text classification', 'named entity', 'language model'],
    'ml':         ['machine learning', 'deep learning', 'xgboost', 'lightgbm',
                   'scikit-learn', 'tensorflow', 'pytorch', 'learning to rank', 'gradient boost'],
}

GOOD_TITLES = ['machine learning', 'ml engineer', 'ai engineer', 'data scientist',
               'nlp engineer', 'research engineer', 'search engineer', 'ranking engineer',
               'applied scientist', 'applied ml', 'staff ml', 'staff engineer',
               'principal engineer', 'senior engineer', 'tech lead', 'backend engineer']

BAD_TITLES  = ['hr manager', 'content writer', 'marketing', 'sales manager', 'recruiter',
               'business analyst', 'product manager', 'graphic designer',
               'accountant', 'finance manager', 'operations manager']

CONSULTING  = ['tcs', 'infosys', 'wipro', 'accenture', 'cognizant', 'capgemini',
               'hcl', 'tech mahindra', 'mphasis', 'hexaware']

LOCATIONS   = ['pune', 'noida', 'hyderabad', 'mumbai', 'delhi', 'bangalore',
               'bengaluru', 'gurugram', 'gurgaon', 'ncr', 'new delhi']


def skill_hits(c: dict) -> dict:
    parts  = [s['name'].lower() for s in c.get('skills', [])]
    parts += [r.get('description', '').lower() for r in c.get('career_history', [])]
    parts += [c.get('profile', {}).get('summary', '').lower()]
    text   = ' '.join(parts)
    return {cat: any(kw in text for kw in kws) for cat, kws in CORE_SKILLS.items()}


def score(c: dict) -> float:
    p   = c.get('profile', {})
    sig = c.get('redrob_signals', {})
    sk  = c.get('skills', [])
    cr  = c.get('career_history', [])
    s   = 0.0
    title = p.get('current_title', '').lower()

    # Title (−30 / 0 / +20)
    for t in GOOD_TITLES:
        if t in title: s += 20; break
    for t in BAD_TITLES:
        if t in title: s -= 30; break

    # YoE
    yoe = p.get('years_of_experience', 0)
    s += {True: 15}.get(5 <= yoe <= 9, 0) or \
         {True: 10}.get(4 <= yoe < 5,  0) or \
         {True:  8}.get(9 < yoe <= 12, 0) or \
         {True:  4}.get(3 <= yoe < 4,  0) or 0

    # Skills
    h  = skill_hits(c)
    s += h['embeddings'] * 8
    s += h['vector_db']  * 7
    s += h['retrieval']  * 6
    s += h['python']     * 3
    s += h['eval']       * 6
    s += h['llm']        * 3
    s += h['nlp']        * 2
    s += h['ml']         * 2

    # Company type
    cos = [r.get('company', '').lower() for r in cr]
    nc  = sum(1 for co in cos if any(f in co for f in CONSULTING))
    if len(cr) > 0:
        s += 15 if nc == 0 else (7 if nc < len(cr) else -15)

    # Location
    loc = p.get('location', '').lower()
    s += 10 if any(l in loc for l in LOCATIONS) else (3 if p.get('country','').lower() == 'india' else 0)

    # Signals
    try:
        la = datetime.strptime(sig.get('last_active_date', '2020-01-01'), '%Y-%m-%d').date()
        d  = (TODAY - la).days
        s += 8 if d <= 30 else (5 if d <= 90 else (2 if d <= 180 else -3))
    except Exception:
        pass

    s += sig.get('recruiter_response_rate', 0) * 6
    s += 3 if sig.get('open_to_work_flag') else 0
    notice = sig.get('notice_period_days', 90)
    s += 3 if notice <= 30 else (1 if notice <= 60 else 0)
    gh = sig.get('github_activity_score', -1)
    s += 3 if gh > 70 else (1 if gh > 40 else 0)

    # Honeypot detection
    if any(r.get('duration_months', 0) > 600 for r in cr): s -= 50
    if sum(1 for sk_ in sk if sk_.get('proficiency') == 'expert' and sk_.get('duration_months', 1) == 0) >= 5:
        s -= 20

    return s


def reasoning(c: dict) -> str:
    p, sig = c.get('profile', {}), c.get('redrob_signals', {})
    h      = skill_hits(c)
    good   = [k for k in ['embeddings','vector_db','retrieval','eval','llm'] if h[k]]
    rr     = sig.get('recruiter_response_rate', 0)
    notice = sig.get('notice_period_days', 90)
    try:
        d = (TODAY - datetime.strptime(sig.get('last_active_date', '2020-01-01'), '%Y-%m-%d').date()).days
        act = f'active {d}d ago'
    except Exception:
        act = 'activity unknown'

    parts = [
        f"{p.get('current_title','')} | {p.get('years_of_experience',0):.1f}yr | {p.get('location','')}",
        f"skills: {', '.join(good[:3]) or 'general ML'}",
        f"response_rate={rr:.0%}",
        act,
        f"notice={notice}d",
    ]
    return '; '.join(parts)[:280]


def rank_candidates(jsonl_path: str, out_csv: str, top_n: int = 100):
    candidates = []
    with open(jsonl_path) as f:
        for line in f:
            line = line.strip()
            if line:
                candidates.append(json.loads(line))

    scored = sorted(((c['candidate_id'], score(c), c) for c in candidates),
                    key=lambda x: (-x[1], x[0]))[:top_n]

    hi, lo = scored[0][1], scored[-1][1]
    span   = hi - lo if hi != lo else 1

    rows = []
    for i, (cid, raw, c) in enumerate(scored):
        rows.append({
            'candidate_id': cid,
            'rank':         i + 1,
            'score':        round(0.5 + 0.499 * (raw - lo) / span, 4),
            'reasoning':    reasoning(c),
        })

    with open(out_csv, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=['candidate_id', 'rank', 'score', 'reasoning'])
        w.writeheader()
        w.writerows(rows)

    print(f"Saved {len(rows)} candidates to {out_csv}")
    return rows


if __name__ == '__main__':
    import sys
    jl  = sys.argv[1] if len(sys.argv) > 1 else 'candidates.jsonl'
    out = sys.argv[2] if len(sys.argv) > 2 else 'submission.csv'
    rank_candidates(jl, out)
