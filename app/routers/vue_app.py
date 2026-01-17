"""Vue.js 3 SPA Router"""
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
import os

router = APIRouter(tags=["vue-app"])

# Serve Vue.js built index.html
@router.get("/app/{full_path:path}", response_class=HTMLResponse, include_in_schema=False)
async def serve_vue_app(request: Request, full_path: str):
    """
    Serve Vue.js 3 SPA for all /app/* routes
    This enables client-side routing with Vue Router
    """
    index_path = "/var/www/agtrmerkezi/static/dist/index.html"

    if os.path.exists(index_path):
        with open(index_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Simple CSRF token injection (if needed)
        # Replace {{ csrf_token() }} placeholder
        if hasattr(request.state, 'csrf_token'):
            content = content.replace(
                "{{ csrf_token() if csrf_token is defined else '' }}",
                request.state.csrf_token
            )
        else:
            content = content.replace(
                "{{ csrf_token() if csrf_token is defined else '' }}",
                ""
            )

        return HTMLResponse(content=content)

    return HTMLResponse(content="<h1>Vue app not built</h1><p>Run: cd frontend && npm run build</p>", status_code=500)


@router.get("/app", response_class=HTMLResponse, include_in_schema=False)
async def serve_vue_app_root(request: Request):
    """Serve Vue.js app root"""
    return await serve_vue_app(request, "")
