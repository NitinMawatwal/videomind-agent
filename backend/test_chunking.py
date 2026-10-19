from chunking import chunk_transcript


def test_chunk_transcript_preserves_timestamps():
    transcript = {
        "content": [
            {
                "text": "A" * 60,
                "offset": 0,
                "duration": 5000,
            },
            {
                "text": "B" * 60,
                "offset": 5000,
                "duration": 5000,
            },
            {
                "text": "C" * 60,
                "offset": 10000,
                "duration": 5000,
            },
        ]
    }

    chunks = chunk_transcript(
        transcript,
        chunk_size=100,
        overlap=20,
    )

    assert len(chunks) >= 2
    assert chunks[0]["start"] == 0
    assert chunks[0]["end"] == 5
    assert all(chunk["text"] for chunk in chunks)