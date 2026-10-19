from groq import AsyncGroq

from backend.config import settings


client = AsyncGroq(api_key=settings.GROQ_API_KEY)

MODEL_NAME = "openai/gpt-oss-120b"

async def generate_answer(question: str, chunks: list[dict]) -> str:
    context = "\n\n".join(
        f"Timestamp: {chunk['start']}s - {chunk['end']}s\n"
        f"Transcript: {chunk['text']}"
        for chunk in chunks
    )

    response = await client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are VideoMind, a helpful video assistant. "
                    "Answer the user's question using only the provided "
                    "transcript context. If the context does not contain "
                    "the answer, clearly say you could not find it in "
                    "the transcript. Be concise and accurate."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Transcript context:\n{context}\n\n"
                    f"Question: {question}"
                ),
            },
        ],
        temperature=0.2,
    )

    return response.choices[0].message.content or ""