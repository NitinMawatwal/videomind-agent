from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl, Field

from backend.retrieval_service import retrieval_service
from backend.transcript_service import fetch_transcript
from backend.chunking import chunk_transcript
from backend.llm_service import generate_answer

app = FastAPI(title="VideoMind Agent")


class IngestRequest(BaseModel):
    video_url: HttpUrl


class AskRequest(BaseModel):
    question: str = Field(min_length=1)
    top_k: int = Field(default=3, ge=1, le=10)


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

        answer = await generate_answer(
            request.question,
            results,
        )

        return {
            "question": request.question,
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