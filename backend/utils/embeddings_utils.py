from ollama import embeddings

def embed_text_with_ollama(text: str):
    """
    Generate embeddings using the local nomic-embed-text model.
    """
    try:
        response = embeddings(model="nomic-embed-text", input=text)
        embedding = response.get("embedding")
        if not embedding:
            raise ValueError("Embedding not found in response")
        return embedding
    except Exception as e:
        print(f"ERROR: Failed to generate embedding with nomic-embed-text: {e}")
        raise
