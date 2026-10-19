import asyncio

import httpx

from backend.config import settings


SUPADATA_BASE_URL = "https://api.supadata.ai/v1"


async def fetch_transcript(video_url: str) -> dict:
    if not settings.SUPADATA_API_KEY:
        raise ValueError("SUPADATA_API_KEY is missing from .env")

    headers = {
        "x-api-key": settings.SUPADATA_API_KEY,
    }

    params = {
        "url": video_url,
        "text": "false",
        "mode": "auto",
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(
            f"{SUPADATA_BASE_URL}/transcript",
            headers=headers,
            params=params,
        )
        response.raise_for_status()

        data = response.json()

        # Short videos may return the transcript immediately.
        if "jobId" not in data:
            return data

        # Long videos may need additional processing.
        job_id = data["jobId"]

        for _ in range(30):
            await asyncio.sleep(2)

            job_response = await client.get(
                f"{SUPADATA_BASE_URL}/transcript/{job_id}",
                headers=headers,
            )
            job_response.raise_for_status()

            job_data = job_response.json()
            status = job_data.get("status")

            if status == "completed":
                result = job_data.get("result")

                if isinstance(result, dict):
                    return result

                return job_data

            if status == "failed":
                raise RuntimeError(
                    f"Supadata transcript job failed: {job_data}"
                )

        raise TimeoutError(
            "Transcript is taking too long. Please try again."
        )