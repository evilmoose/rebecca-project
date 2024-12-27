from numpy import dot
from numpy.linalg import norm
from utils.db_utils import search_ltm
from utils.embeddings_utils import embed_text_with_ollama

def score_memory(memory, is_stm, user_input_embedding, recency_boost=0.4):
    # Compute cosine similarity
    embedding = memory["embedding"]
    similarity = dot(embedding, user_input_embedding) / (norm(embedding) * norm(user_input_embedding))

    # Apply recency boost for STM
    recency = recency_boost if is_stm else 0

    # Consider metadata importance
    meta_importance = memory.get("metadata", {}).get("importance", 0) * 0.1

    return recency + (0.6 * similarity) + meta_importance

def combine_and_prioritize_memories(user_id, user_input, short_term_memory):
    # Generate embeddings for user input
    user_input_embedding = embed_text_with_ollama(user_input)

    # Fetch and score STM
    stm_memories = short_term_memory.load_memory_variables({})["chat_history"]
    stm_scores = [{"text": m["content"], "score": score_memory(m, True, user_input_embedding)} for m in stm_memories]

    # Fetch and score LTM
    ltm_memories = search_ltm(user_id, user_input)
    ltm_scores = [{"text": m["prompt"], "score": score_memory(m, False, user_input_embedding)} for m in ltm_memories]

    # Combine and prioritize
    all_scores = stm_scores + ltm_scores
    best_memory = max(all_scores, key=lambda x: x["score"])

    # Inject high-priority LTM into STM
    if best_memory in ltm_scores:
        short_term_memory.save_context({"user": "System"}, {"system": best_memory["text"]})

    return short_term_memory
