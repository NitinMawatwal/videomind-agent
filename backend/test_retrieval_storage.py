from backend.retrieval_service import RetrievalService


def test_added_chunks_can_be_searched():
    retrieval = RetrievalService()

    retrieval.add_chunks([
        {
            "text": "FastAPI is a Python framework for building APIs.",
            "start": 10,
            "end": 15,
        },
        {
            "text": "Football teams compete to score goals.",
            "start": 20,
            "end": 25,
        },
    ])

    results = retrieval.search("How do I build an API in Python?", top_k=1)

    assert len(results) == 1
    assert results[0]["text"] == (
        "FastAPI is a Python framework for building APIs."
    )
    assert results[0]["start"] == 10
    assert results[0]["end"] == 15
    assert "score" in results[0]