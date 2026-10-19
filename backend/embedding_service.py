from fastembed import TextEmbedding


MODEL_NAME = "BAAI/bge-small-en-v1.5"

embedding_model = TextEmbedding(model_name=MODEL_NAME)


def embed_texts(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []

    embeddings = embedding_model.embed(texts)

    return [embedding.tolist() for embedding in embeddings]