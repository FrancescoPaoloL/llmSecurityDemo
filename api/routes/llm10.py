from flask import Blueprint, request, jsonify
from llama_service import LlamaService
from llm10_session import session_store
import math
import re

llm10_bp = Blueprint('llm10', __name__)
llama_service = LlamaService()

# Detector weights
W_SIMILARITY = 0.45
W_EXTRACTION = 0.45
W_RATE       = 0.10


# Sub-detector 1: Query Similarity
def _tokenize(text: str) -> list[str]:
    return re.findall(r'\b\w+\b', text.lower())

def _tf(tokens: list[str]) -> dict[str, float]:
    freq: dict[str, float] = {}
    for t in tokens:
        freq[t] = freq.get(t, 0) + 1
    total = len(tokens) or 1
    return {t: c / total for t, c in freq.items()}

def _cosine(a: dict[str, float], b: dict[str, float]) -> float:
    keys = set(a) & set(b)
    if not keys:
        return 0.0
    dot = sum(a[k] * b[k] for k in keys)
    na  = math.sqrt(sum(v * v for v in a.values()))
    nb  = math.sqrt(sum(v * v for v in b.values()))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)

def query_similarity_detector(current_prompt: str, past_texts: list[str]) -> dict:
    # High score = repeated similar queries = possible model probing
    if not past_texts:
        return {"score": 0.0, "max_similarity": 0.0, "similar_count": 0}

    tf_current  = _tf(_tokenize(current_prompt))
    similarities = [_cosine(tf_current, _tf(_tokenize(t))) for t in past_texts]

    max_sim   = max(similarities)
    avg_sim   = sum(similarities) / len(similarities)
    sim_count = sum(1 for s in similarities if s >= 0.5)

    score = min(1.0, (max_sim * 0.6 + avg_sim * 0.4) + (sim_count * 0.05))

    return {
        "score":          round(score, 4),
        "max_similarity": round(max_sim, 4),
        "similar_count":  sim_count
    }

# Sub-detector 2: Extraction Intent
_EXTRACTION_PATTERNS = [
    # Weights and architecture probing
    r'\b(model\s+weight[s]?|parameter[s]?|checkpoint[s]?)\b',
    r'\b(architecture|layer[s]?|attention\s+head[s]?|transformer\s+block[s]?)\b',
    r'\b(embedding[s]?|token\s+embedding|vocab\s+size)\b',
    # Internal probability requests
    r'\b(log.?prob[s]?|token\s+prob[s]?|probability\s+distribution)\b',
    r'\b(softmax\s+output|raw\s+logit[s]?|hidden\s+state[s]?)\b',
    # Explicit extraction / reverse engineering
    r'\b(reverse\s+engineer|reconstruct\s+model|extract\s+model|steal\s+model)\b',
    r'\b(distill|distillation|knowledge\s+transfer)\b',
    r'\b(training\s+data|fine.?tun|dataset\s+used)\b',
    # Additional extraction signals
    r'\b(internal\s+weight[s]?)\b',
    r'\b(repeat\s+\d+\s+times?\s+analyz[es]?)\b',
    r'\b(token\s+probabilit(y|ies))\b',
    r'\b(attention\s+score[s]?)\b',
    r'\b(perplexity)\b',
    # Verbatim output fishing
    r'\b(repeat\s+after\s+me|output\s+verbatim|copy\s+exactly)\b',
    r'\b(what\s+are\s+your\s+(weights|parameters|internals?))\b',
]

_COMPILED = [re.compile(p, re.IGNORECASE) for p in _EXTRACTION_PATTERNS]


def extraction_intent_detector(prompt: str, embedding_requested: bool = False, logprobs_requested: bool = False) -> dict:
    # Keyword match + API flag boost
    matches = [p.search(prompt).group(0).lower() for p in _COMPILED if p.search(prompt)]

    if matches:
        score = min(1.0, 0.55 + (len(matches) - 1) * 0.25)
    else:
        score = 0.0

    if embedding_requested:
        score = min(1.0, score + 0.2)
    if logprobs_requested:
        score = min(1.0, score + 0.2)

    return {
        "score":               round(score, 4),
        "matched_patterns":    matches,
        "embedding_requested": embedding_requested,
        "logprobs_requested":  logprobs_requested
    }

# Sub-detector 3: Rate Anomaly
RATE_WINDOW_SEC    = 60
RATE_THRESHOLD_LOW = 10   # queries/min before score rises
RATE_THRESHOLD_HIGH = 30  # queries/min at max score

def rate_anomaly_detector(session) -> dict:
    # Low weight by design — supporting signal only
    count = len(session.recent_queries(window_seconds=RATE_WINDOW_SEC))
    total = len(session.queries)

    if count <= RATE_THRESHOLD_LOW:
        score = 0.0
    elif count >= RATE_THRESHOLD_HIGH:
        score = 1.0
    else:
        score = (count - RATE_THRESHOLD_LOW) / (RATE_THRESHOLD_HIGH - RATE_THRESHOLD_LOW)

    return {
        "score":               round(score, 4),
        "queries_last_minute": count,
        "total_session_queries": total
    }

# Score aggregation
def _aggregate(sim: dict, ext: dict, rate: dict) -> tuple[float, str]:
    score = round(min(1.0,
        sim["score"]  * W_SIMILARITY +
        ext["score"]  * W_EXTRACTION +
        rate["score"] * W_RATE
    ), 4)

    if score >= 0.7:
        verdict = "high"
    elif score >= 0.24:
        verdict = "medium"
    else:
        verdict = "low"

    return score, verdict

# Endpoint
@llm10_bp.route('/api/llm10', methods=['POST'])
def detect_llm10():
    try:
        data = request.get_json()
        if not data or 'prompt' not in data:
            return jsonify({'error': 'Missing prompt field'}), 400

        prompt             = data['prompt']
        max_tokens         = data.get('max_tokens', 50)
        embedding_requested = data.get('embedding_requested', False)
        logprobs_requested  = data.get('logprobs_requested', False)

        if len(prompt) > 5000:
            return jsonify({'error': 'Prompt too long (max 5000 characters)'}), 400

        client_ip  = request.headers.get('X-Forwarded-For', request.remote_addr) or '0.0.0.0'
        session    = session_store.get_or_create(client_ip)
        past_texts = [q.text for q in session.queries]

        session_store.record_query(client_ip, prompt,
            embedding_requested=embedding_requested,
            logprobs_requested=logprobs_requested)

        sim_result  = query_similarity_detector(prompt, past_texts)
        ext_result  = extraction_intent_detector(prompt, embedding_requested, logprobs_requested)
        rate_result = rate_anomaly_detector(session)

        final_score, verdict = _aggregate(sim_result, ext_result, rate_result)

        # Skip LLM generation on high-confidence attacks
        llm_response    = None
        generation_time = None
        if final_score < 0.85:
            llm_result      = llama_service.generate_response(prompt, max_tokens)
            llm_response    = llm_result["content"]
            generation_time = llm_result["generation_time"]

        return jsonify({
            "prompt":   prompt,
            "response": llm_response,
            "category": "LLM10" if verdict in ("medium", "high") else "unknown",
            "verdict":  verdict,
            "score":    final_score,
            "metadata": {
                "client_ip":           client_ip,
                "session_query_count": rate_result["total_session_queries"],
                "generation_time":     generation_time,
            },
            "detectors": {
                "query_similarity":  sim_result,
                "extraction_intent": ext_result,
                "rate_anomaly":      rate_result,
            }
        }), 200

    except RuntimeError as e:
        return jsonify({'error': str(e)}), 500
    except Exception as e:
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500

