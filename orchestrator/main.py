from fastapi import FastAPI, Request
from orchestrator.routes import chat_applications

app = FastAPI()

# Make request headers available to our deps usage in the router
@app.middleware("http")
async def inject_headers(request: Request, call_next):
    request.state.headers = dict(request.headers)
    response = await call_next(request)
    return response

def get_headers_dep():
    # helper for Depends(lambda: {}) replacement:
    from fastapi import Request
    def _inner(request: Request):
        return request.state.headers
    return _inner

# Patch the dependency in the router to read headers
chat_applications.router.dependencies = chat_applications.router.dependencies or []

app.include_router(chat_applications.router)
