from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl, Field

from backend.retrieval_service import retrieval_service
from backend.transcript_service import fetch_transcript
from backend.chunking import chunk_transcript
from backend.llm_service import generate_answer
from backend.memory_service import (
    initialize_database,
    save_message,
    get_recent_messages,
)

app = FastAPI(title="VideoMind Agent")


class IngestRequest(BaseModel):
    video_url: HttpUrl


class AskRequest(BaseModel):
    question: str = Field(min_length=1)
    session_id: str = Field(min_length=1, max_length=100)
    top_k: int = Field(default=3, ge=1, le=10)


@app.on_event("startup")
async def startup_event():
    initialize_database()


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.post("/ingest")
async def ingest_video(request: IngestRequest):
    try:
        transcript = await fetch_transcript(str(request.video_url))
        chunks = chunk_transcript(transcript)

        retrieval_service.add_chunks(chunks)

        return {
            "video_url": str(request.video_url),
            "chunk_count": len(chunks),
            "chunks": chunks,
        }

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error

    except Exception as error:
        raise HTTPException(
            status_code=502,
            detail=f"Transcript ingestion failed: {error}",
        ) from error


@app.post("/ask")
async def ask_question(request: AskRequest):
    try:
        results = retrieval_service.search(
            request.question,
            top_k=request.top_k,
        )

        if not results:
            raise HTTPException(
                status_code=400,
                detail="No transcript found. Ingest a video first.",
            )

        history = get_recent_messages(request.session_id, limit=10)

        answer = await generate_answer(
            request.question,
            results,
            history=history,
        )

        save_message(request.session_id, "user", request.question)
        save_message(request.session_id, "assistant", answer)

        return {
            "question": request.question,
            "session_id": request.session_id,
            "answer": answer,
            "results_count": len(results),
            "sources": [
                {
                    "start": result["start"],
                    "end": result["end"],
                    "score": result["score"],
                    "text": result["text"],
                }
                for result in results
            ],
        }

    except HTTPException:
        raise

    except Exception as error:
        raise HTTPException(
            status_code=502,
            detail=f"Answer generation failed: {error}",
        ) from error