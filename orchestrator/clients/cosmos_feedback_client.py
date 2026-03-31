import os
import logging
from typing import Optional, List, Dict, Any, Tuple

from azure.cosmos.aio import CosmosClient
from azure.identity import DefaultAzureCredential

logger = logging.getLogger(__name__)


class CosmosFeedbackClient:
    """
    Async CosmosDB client for the unified feedback container.

    All feedback — regardless of which app submitted it — is written here so
    the admin panel has a single place to query.

    Required env vars:
        AZURE_COSMOSDB_ACCOUNT         CosmosDB account name
        AZURE_COSMOSDB_DATABASE        Database name
    Optional env vars:
        AZURE_COSMOSDB_ACCOUNT_KEY     Account key (falls back to DefaultAzureCredential)
        AZURE_COSMOSDB_FEEDBACK_CONTAINER  Container name (default: "feedback")
    """

    def __init__(self):
        account = os.getenv("AZURE_COSMOSDB_ACCOUNT", "")
        key = os.getenv("AZURE_COSMOSDB_ACCOUNT_KEY", "")
        self.database_name = os.getenv("AZURE_COSMOSDB_DATABASE", "")
        self.container_name = os.getenv("AZURE_COSMOSDB_FEEDBACK_CONTAINER", "feedback")

        if not account or not self.database_name:
            raise ValueError(
                "CosmosDB not configured. "
                "Set AZURE_COSMOSDB_ACCOUNT and AZURE_COSMOSDB_DATABASE."
            )

        endpoint = f"https://{account}.documents.azure.com:443/"
        credential = key if key else DefaultAzureCredential()
        self._client = CosmosClient(endpoint, credential=credential)
        self._container = (
            self._client
            .get_database_client(self.database_name)
            .get_container_client(self.container_name)
        )

    async def upsert(self, record: Dict[str, Any]) -> Dict[str, Any]:
        return await self._container.upsert_item(record)

    async def query(
        self,
        session_id: Optional[str] = None,
        feedback_type: Optional[str] = None,
        source_app: Optional[str] = None,
        limit: int = 100,
        skip: int = 0,
    ) -> Tuple[List[Dict], int]:
        conditions = ["c.type = 'feedback'"]
        params: List[Dict] = []

        if session_id:
            conditions.append("c.session_id = @session_id")
            params.append({"name": "@session_id", "value": session_id})
        if feedback_type:
            conditions.append("c.feedback_type = @feedback_type")
            params.append({"name": "@feedback_type", "value": feedback_type})
        if source_app:
            conditions.append("c.source_app = @source_app")
            params.append({"name": "@source_app", "value": source_app})

        where = " AND ".join(conditions)

        count_q = f"SELECT VALUE COUNT(1) FROM c WHERE {where}"
        total = 0
        async for item in self._container.query_items(query=count_q, parameters=params):
            total = item

        data_q = (
            f"SELECT * FROM c WHERE {where} "
            f"ORDER BY c.timestamp DESC OFFSET {skip} LIMIT {limit}"
        )
        results: List[Dict] = []
        async for item in self._container.query_items(query=data_q, parameters=params):
            results.append(item)

        return results, total

    async def get_stats(self) -> Dict[str, Any]:
        query = (
            "SELECT c.feedback_type, c.source_app, c.intent "
            "FROM c WHERE c.type = 'feedback'"
        )
        rows: List[Dict] = []
        async for item in self._container.query_items(query=query):
            rows.append(item)

        thumbs_up = sum(1 for r in rows if r.get("feedback_type") == "thumbs_up")
        thumbs_down = sum(1 for r in rows if r.get("feedback_type") == "thumbs_down")
        total = len(rows)
        satisfaction = round(thumbs_up / total * 100, 2) if total > 0 else 0

        by_intent: Dict[str, Dict] = {}
        for r in rows:
            intent = r.get("intent") or "unknown"
            by_intent.setdefault(intent, {"thumbs_up": 0, "thumbs_down": 0, "total": 0})
            by_intent[intent]["total"] += 1
            if r.get("feedback_type") == "thumbs_up":
                by_intent[intent]["thumbs_up"] += 1
            elif r.get("feedback_type") == "thumbs_down":
                by_intent[intent]["thumbs_down"] += 1

        return {
            "total_feedback": total,
            "thumbs_up": thumbs_up,
            "thumbs_down": thumbs_down,
            "satisfaction_rate": satisfaction,
            "by_intent": by_intent,
        }

    async def close(self):
        await self._client.close()


# ---------------------------------------------------------------------------
# Module-level singleton — lazily initialised so missing env vars in local
# dev don't crash the app at import time.
# ---------------------------------------------------------------------------
_client: Optional["CosmosFeedbackClient"] = None
_init_attempted = False


def get_feedback_client() -> Optional["CosmosFeedbackClient"]:
    """Return the CosmosDB feedback client, or None if not configured."""
    global _client, _init_attempted
    if not _init_attempted:
        _init_attempted = True
        try:
            _client = CosmosFeedbackClient()
            logger.info("CosmosFeedbackClient initialised successfully.")
        except Exception as exc:
            logger.warning(
                "CosmosDB feedback client unavailable (%s). "
                "Falling back to in-memory store.",
                exc,
            )
            _client = None
    return _client
