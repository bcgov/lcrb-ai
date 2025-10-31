import httpx
from fastapi import Depends
from orchestrator.clients.portal_api import PortalApi
import os

PORTAL_BASE = os.getenv("PORTAL_BASE_URL", "https://dev.justice.gov.bc.ca/lcrb")

async def get_http_client():
    async with httpx.AsyncClient(timeout=30) as client:
        yield client

def get_portal_api() -> PortalApi:
    return PortalApi(PORTAL_BASE)
