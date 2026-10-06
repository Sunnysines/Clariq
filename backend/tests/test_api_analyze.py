"""API integration tests for analysis endpoints."""
from unittest.mock import patch, AsyncMock
import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.database.session import init_db


@pytest.mark.asyncio
async def test_start_analysis_and_poll():
    await init_db()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Patch background task so test does not fire live external SerpApi requests
        with patch("app.api.analyze.run_analysis_pipeline", new_callable=AsyncMock):
            resp = await client.post(
                "/api/analyze",
                json={"question": "Which Indian city is best for an entry-level AI/ML career in 2026?"},
            )
            assert resp.status_code == 200
            data = resp.json()
            assert "analysis_id" in data
            assert data["status"] == "processing"
            analysis_id = data["analysis_id"]

            # Poll status
            poll_resp = await client.get(f"/api/analyze/{analysis_id}")
            assert poll_resp.status_code == 200
            poll_data = poll_resp.json()
            assert poll_data["id"] == analysis_id
            assert "AI/ML career" in poll_data["question"]

            # Query evidence, signals, entities endpoints
            ev_resp = await client.get(f"/api/analyze/{analysis_id}/evidence")
            assert ev_resp.status_code == 200
            assert "items" in ev_resp.json()

            sig_resp = await client.get(f"/api/analyze/{analysis_id}/signals")
            assert sig_resp.status_code == 200
            assert "items" in sig_resp.json()

            ent_resp = await client.get(f"/api/analyze/{analysis_id}/entities")
            assert ent_resp.status_code == 200
            assert "items" in ent_resp.json()


@pytest.mark.asyncio
async def test_analysis_not_found():
    await init_db()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/analyze/non-existent-id")
        assert resp.status_code == 404
