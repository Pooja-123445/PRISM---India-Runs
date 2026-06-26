"""
PRISM — JD Parser
Extracts structured signals from raw job description text.
"""

import re


JD_SIGNALS = {
    'must_have_skills': [
        'embeddings', 'vector database', 'python', 'retrieval', 'ranking',
        'evaluation framework', 'ndcg', 'mrr', 'semantic search', 'rag',
    ],
    'nice_to_have': [
        'llm', 'fine-tuning', 'distributed systems', 'open source',
        'kubernetes', 'mlops', 'pytorch', 'huggingface',
    ],
    'experience_range': (5, 9),
    'preferred_locations': ['pune', 'noida', 'hyderabad', 'mumbai', 'delhi ncr', 'bangalore'],
    'company_type': 'product',
    'role_type': 'founding team',
}


def parse_jd(text: str) -> dict:
    """Extract key signals from a job description string."""
    text_lower = text.lower()

    found_must   = [s for s in JD_SIGNALS['must_have_skills']   if s in text_lower]
    found_nice   = [s for s in JD_SIGNALS['nice_to_have']       if s in text_lower]
    found_locs   = [l for l in JD_SIGNALS['preferred_locations'] if l in text_lower]

    # Extract YoE range
    yoe_pattern = re.findall(r'(\d+)[–\-]\s*(\d+)\s*(?:years?|yrs?)', text_lower)
    yoe_range   = tuple(map(int, yoe_pattern[0])) if yoe_pattern else JD_SIGNALS['experience_range']

    return {
        'must_have_skills':    found_must,
        'nice_to_have_skills': found_nice,
        'preferred_locations': found_locs,
        'experience_range':    yoe_range,
        'company_type':        'product' if 'product' in text_lower else 'any',
        'founding_team':       'founding' in text_lower,
    }


if __name__ == '__main__':
    sample = """
    Senior AI Engineer – Founding Team at Redrob AI (Pune/Noida, 5–9 yrs).
    Must have: embeddings-based retrieval, vector database (Pinecone/Qdrant/FAISS),
    Python, evaluation frameworks (NDCG, MRR), semantic search, RAG pipelines.
    Nice to have: LLM fine-tuning, HuggingFace, distributed systems.
    """
    import json
    print(json.dumps(parse_jd(sample), indent=2))
