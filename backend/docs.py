import json
from pathlib import Path
from urllib.parse import urlparse, urlunparse

from django.http import HttpResponse, HttpResponseNotFound
from django.urls import reverse
from django.views.decorators.http import require_GET

BASE_DIR = Path(__file__).resolve().parent
OPENAPI_PATH = BASE_DIR / "openapi.json"


@require_GET
def openapi_json(request):
    """
    Serve the static OpenAPI schema used by Swagger UI.
    """
    if not OPENAPI_PATH.exists():
        return HttpResponseNotFound("openapi.json not found")
    data = OPENAPI_PATH.read_text(encoding="utf-8")
    return HttpResponse(data, content_type="application/json")


@require_GET
def swagger_ui(request):
    """
    Minimal Swagger UI powered by the static OpenAPI document.
    Uses the CDN-hosted swagger-ui bundle (no extra python deps).
    """
    schema_url = request.build_absolute_uri(reverse("openapi-json"))
    forwarded_proto = request.META.get("HTTP_X_FORWARDED_PROTO")
    if forwarded_proto in ("http", "https"):
        parsed = urlparse(schema_url)
        if parsed.scheme != forwarded_proto:
            schema_url = urlunparse(parsed._replace(scheme=forwarded_proto))
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Swagger UI</title>
  <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css">
</head>
<body>
  <div id="swagger-ui"></div>
  <script src="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
  <script>
    window.onload = function() {{
      SwaggerUIBundle({{
        url: "{schema_url}",
        dom_id: '#swagger-ui',
        presets: [SwaggerUIBundle.presets.apis],
      }});
    }};
  </script>
</body>
</html>"""
    return HttpResponse(html, content_type="text/html")
