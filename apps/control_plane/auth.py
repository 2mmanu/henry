import hmac
from typing import Protocol

from fastapi import HTTPException, Request

from henry.contracts.task import SubjectContext


class IdentityProvider(Protocol):
    async def authenticate(self, request: Request) -> SubjectContext: ...


class HeaderIdentityProvider:
    """Development adapter for identity asserted by a trusted upstream gateway."""

    def __init__(self, api_key: str) -> None:
        self._api_key = api_key

    async def authenticate(self, request: Request) -> SubjectContext:
        if not self._api_key:
            raise HTTPException(503, detail="HENRY_API_KEY is not configured")
        supplied_key = request.headers.get("X-HEnRY-Key", "")
        if not hmac.compare_digest(supplied_key, self._api_key):
            raise HTTPException(401, detail="Invalid HEnRY API key")

        subject_id = request.headers.get("X-HEnRY-Subject", "")
        tenant_id = request.headers.get("X-HEnRY-Tenant", "")
        if not subject_id or not tenant_id:
            raise HTTPException(401, detail="Subject and tenant headers are required")
        entitlements = frozenset(
            item.strip()
            for item in request.headers.get("X-HEnRY-Entitlements", "").split(",")
            if item.strip()
        )
        return SubjectContext(
            subject_id=subject_id,
            tenant_id=tenant_id,
            entitlements=entitlements,
        )
