from backend.retrieval_service import RetrievalService


def test_retrieval_finds_relevant_chunks():
    retrieval = RetrievalService()

    retrieval.add_chunks([
        {
            "text": "Python is a programming language used to build software.",
            "start": 0,
            "end": 5,
        },
        {
            "text": "Football teams compete to score goals.",
            "start": 5,
            "end": 10,
        },
        {
            "text": "FastAPI is a Python framework for building APIs.",
            "start": 10,
            "end": 15,
        },
    ])

    results = retrieval.search(
        "How can I build an API with Python?",
        top_k=2,
    )

    assert len(results) == 2
    assert "FastAPI" in results[0]["text"] or "Python" in results[0]["text"]
    assert all("score" in result for result in results)