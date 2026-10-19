def chunk_transcript(
    transcript: dict,
    chunk_size: int = 1000,
    overlap: int = 200,
) -> list[dict]:
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")

    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be >= 0 and smaller than chunk_size")

    segments = transcript.get("content", [])

    if not isinstance(segments, list):
        raise ValueError(
            "Expected timestamped transcript segments. "
            "Make sure the API request uses text=false."
        )

    chunks = []
    current_segments = []
    current_length = 0

    for segment in segments:
        text = segment.get("text", "").strip()

        if not text:
            continue

        segment_length = len(text)

        if current_segments and current_length + segment_length > chunk_size:
            chunks.append(
                {
                    "text": " ".join(
                        item["text"] for item in current_segments
                    ),
                    "start": current_segments[0]["start"],
                    "end": current_segments[-1]["end"],
                }
            )

            # Keep the final segments to create overlap.
            while (
                current_segments
                and current_length > overlap
            ):
                removed = current_segments.pop(0)
                current_length -= len(removed["text"])

            current_length = sum(
                len(item["text"]) for item in current_segments
            )

        current_segments.append(
            {
                "text": text,
                "start": segment.get("offset", 0) / 1000,
                "end": (
                    segment.get("offset", 0)
                    + segment.get("duration", 0)
                ) / 1000,
            }
        )
        current_length += segment_length

    if current_segments:
        chunks.append(
            {
                "text": " ".join(item["text"] for item in current_segments),
                "start": current_segments[0]["start"],
                "end": current_segments[-1]["end"],
            }
        )

    return chunks