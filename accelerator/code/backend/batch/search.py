import logging
import json
import requests
import azure.functions as func
from utilities.helpers.env_helper import EnvHelper
from openai import AzureOpenAI

bp_search = func.Blueprint()

@bp_search.route(route="search", methods=["POST", "OPTIONS"], auth_level=func.AuthLevel.ANONYMOUS)
def search_documents(req: func.HttpRequest) -> func.HttpResponse:
    if req.method == "OPTIONS":
        return func.HttpResponse(
            "",
            status_code=200,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Max-Age": "86400"
            }
        )

    logging.info('Processing AI public search request (via Azure Function).')
    env_helper = EnvHelper()
    try:
        body = req.get_json()
    except ValueError:
        body = {}
    query = body.get('query', '')
    index = body.get('index', env_helper.AZURE_SEARCH_INDEX)
    top_k = int(body.get('top', 3))

    search_url = f"{env_helper.AZURE_SEARCH_SERVICE}/indexes/{index}/docs/search?api-version=2021-04-30-Preview"
    if env_helper.is_auth_type_keys():
        headers = {'api-key': env_helper.AZURE_SEARCH_KEY, 'Content-Type': 'application/json'}
    else:
        token = env_helper.AZURE_TOKEN_PROVIDER.get_token().token
        headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}

    payload = {
        'search': query,
        'top': top_k,
        'queryType': 'semantic',
        'semanticConfiguration': env_helper.AZURE_SEARCH_SEMANTIC_SEARCH_CONFIG,
        'captions': 'extractive'
    }

    resp = requests.post(search_url, headers=headers, json=payload)
    search_json = resp.json()

    snippets = []
    for idx, doc in enumerate(search_json.get('value', [])):
        caption = doc.get('@search.captions', [{}])[0].get('text', '')
        title = doc.get(env_helper.AZURE_SEARCH_TITLE_COLUMN) or f'Document {idx+1}'
        url = doc.get(env_helper.AZURE_SEARCH_SOURCE_COLUMN)
        snippets.append({
            'id': doc.get(env_helper.AZURE_SEARCH_FIELDS_ID),
            'title': title,
            'snippet': caption,
            'url': url
        })

    system_prompt = (
        'You are an assistant for the BC Liquor and Cannabis Regulation Branch. '
        'Provide accurate, clear answers using the documents below.'
    )
    snippet_text = '\n'.join(f"{i+1}. {s['title']}: {s['snippet']}" for i, s in enumerate(snippets))
    user_prompt = f"User question: {query}\n\nSearch snippets:\n{snippet_text}\n\nSummarize the answer in 3-4 sentences."

    if env_helper.is_auth_type_keys():
        openai_client = AzureOpenAI(
            azure_endpoint=env_helper.AZURE_OPENAI_ENDPOINT,
            api_version=env_helper.AZURE_OPENAI_API_VERSION,
            api_key=env_helper.AZURE_OPENAI_API_KEY,
        )
    else:
        openai_client = AzureOpenAI(
            azure_endpoint=env_helper.AZURE_OPENAI_ENDPOINT,
            api_version=env_helper.AZURE_OPENAI_API_VERSION,
            azure_ad_token_provider=env_helper.AZURE_TOKEN_PROVIDER,
        )

    completion = openai_client.chat.completions.create(
        model=env_helper.AZURE_OPENAI_MODEL,
        messages=[
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_prompt}
        ],
        temperature=0.2,
        max_tokens=500
    )

    summary = completion.choices[0].message.content
    return func.HttpResponse(
        json.dumps({'summary': summary, 'results': snippets}),
        status_code=200,
        mimetype="application/json",
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type"
            }
    )
