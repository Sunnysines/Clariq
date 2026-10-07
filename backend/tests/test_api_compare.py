"""API tests for the /api/compare endpoint."""
from unittest.mock import patch, AsyncMock
import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.database.session import init_db


@pytest.mark.asyncio
async def test_start_compare_endpoint():
    await init_db()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        with patch("app.api.compare.run_analysis_pipeline", new_callable=AsyncMock):
            resp = await client.post(
                "/api/compare",
                json={
                    "question": "Which Indian city is best for an entry-level AI/ML career in 2026?",
                    "entities": ["Bengaluru", "Hyderabad", "Pune", "Chennai"],
                    "mode": "career",
                },
            )
            assert resp.status_code == 200
            data = resp.json()
            assert "analysis_id" in data
            assert data["status"] == "processing"
