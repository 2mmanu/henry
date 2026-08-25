from __future__ import annotations

from typing import Any

import httpx


class OmniAgentError(RuntimeError):
    pass


class OmniAgentClient:
    def __init__(
        self,
        base_url: str,
        api_key: str,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self._client = httpx.AsyncClient(
            base_url=base_url.rstrip("/"),
            headers={"X-OmniAgent-Key": api_key},
            timeout=30,
            transport=transport,
        )

    async def close(self) -> None:
        await self._client.aclose()

    async def create_session(self, agent_name: str, agent_version: str) -> dict[str, Any]:
        return await self._request(
            "POST",
            "/sessions",
            json={"agent_name": agent_name, "agent_version": agent_version},
        )

    async def run_session(self, session_id: str, prompt: str) -> dict[str, Any]:
        return await self._request(
            "POST",
            f"/sessions/{session_id}/run",
            json={"prompt": prompt, "files": []},
        )

    async def get_session_status(self, session_id: str) -> dict[str, Any]:
        return await self._request("GET", f"/sessions/{session_id}/status")

    async def cancel_session(self, session_id: str) -> None:
        await self._request("POST", f"/sessions/{session_id}/cancel", expect_json=False)

    async def _request(
        self,
        method: str,
        path: str,
        *,
        json: dict[str, Any] | None = None,
        expect_json: bool = True,
    ) -> dict[str, Any]:
        try:
            response = await self._client.request(method, path, json=json)
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise OmniAgentError(f"OmniAgent request failed: {method} {path}: {exc}") from exc
        if not expect_json or response.status_code == 204:
            return {}
        try:
            return response.json()
        except ValueError as exc:
            raise OmniAgentError(f"OmniAgent returned invalid JSON: {method} {path}") from exc
