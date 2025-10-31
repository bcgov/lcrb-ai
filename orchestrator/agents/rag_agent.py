from dotenv import load_dotenv
import os
from typing import Optional, Dict, Any

from openai import AzureOpenAI
from azure.search.documents import SearchClient
from azure.identity import DefaultAzureCredential
from azure.core.credentials import AzureKeyCredential
import httpx

# --- Config (env) ---
load_dotenv()

AOAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AOAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AOAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")
AOAI_CHAT_DEPLOYMENT = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT")

AZ_SEARCH_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT")
AZ_SEARCH_API_KEY = os.getenv("AZURE_SEARCH_API_KEY")
PORTAL_INDEX = "portal-index"


def _aoai_client() -> AzureOpenAI:
    return AzureOpenAI(
        azure_endpoint=AOAI_ENDPOINT,
        api_key=AOAI_API_KEY,
        api_version=AOAI_API_VERSION,
    )


async def answer(query: str,
                 session_id: Optional[str] = None,
                 selected_index: Optional[str] = None) -> Dict[str, Any]:
    """
    General chat over Azure Search (your portal index) using Azure OpenAI 'on your data'.
    Stateless: no chat history included (MVP).
    """
    index = selected_index or PORTAL_INDEX
    missing = [k for k, v in {
        "AZURE_OPENAI_ENDPOINT": AOAI_ENDPOINT,
        "AZURE_OPENAI_CHAT_DEPLOYMENT": AOAI_CHAT_DEPLOYMENT,
        "AZURE_SEARCH_ENDPOINT": AZ_SEARCH_ENDPOINT,
        "PORTAL_INDEX": index,
    }.items() if not v]
    if missing:
        return {"error": "misconfigured", "detail": f"Missing: {', '.join(missing)}"}

    system_msg = (
        "You are an assistant for the BC Liquor and Cannabis Regulation Branch. "
        "Answer clearly and concisely using the connected documents. If unsure, say so."
    )

    try:
        search_client = SearchClient(endpoint=AZ_SEARCH_ENDPOINT,
                             index_name="portal-index",
                             credential=AzureKeyCredential(AZ_SEARCH_API_KEY))


        results = search_client.search(search_text=query, top=5)
        snippets = []
        for i, doc in enumerate(results):
            title = doc.get("title") or doc.get("metadata_storage_name") or f"Document {i+1}"
            preview = (doc.get("content") or "")[:300]
            snippets.append(f"{i+1}. {title}: {preview}")

        snippet_text = "\n".join(snippets) or "(no relevant snippets found)"

        client = _aoai_client()
        resp = client.chat.completions.create(
            model=AOAI_CHAT_DEPLOYMENT,
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": f"User question: {query}\n\nSnippets:\n{snippet_text}\n\nAnswer in 3–4 concise sentences."},
            ],
            temperature=0.2,
            max_tokens=700,
        )

        answer = resp.choices[0].message.content
        return {"answer": answer}
    except Exception as e:
        return {"error": "rag_failed", "detail": str(e)}
