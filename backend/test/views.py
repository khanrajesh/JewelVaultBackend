from django.db import connection
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_GET, require_http_methods

from backend.firebase.firebase import db


@require_GET
def ping_view(request):
    return JsonResponse({"status": "ok"})


@require_GET
def root_message(request):
    return HttpResponse("Up and running boss!")


@require_GET
def list_users(request):
    """
    Fetch all user documents from Firestore collection 'users'.
    """
    try:
        docs = db.collection("users").stream()
        users = []
        for doc in docs:
            data = doc.to_dict() or {}
            data["id"] = doc.id
            users.append(data)
        return JsonResponse({"users": users})
    except Exception as exc:  # pragma: no cover - defensive logging surface
        return JsonResponse({"error": str(exc)}, status=500)


@require_GET
def list_vault_samples(request):
    """
    Fetch sample rows from PostgreSQL table `vault_samples`.
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, name, note, created_at
                FROM vault_samples
                ORDER BY id
                """
            )
            rows = cursor.fetchall()
        samples = [
            {
                "id": row[0],
                "name": row[1],
                "note": row[2],
                "created_at": row[3].isoformat() if row[3] else None,
            }
            for row in rows
        ]
        return JsonResponse({"samples": samples})
    except Exception as exc:  # pragma: no cover - defensive logging surface
        return JsonResponse({"error": str(exc)}, status=500)


@require_http_methods(["GET", "POST"])
def seed_vault_samples(request):
    """
    Create the `vault_samples` table and insert sample rows.
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS vault_samples (
                    id SERIAL PRIMARY KEY,
                    name TEXT NOT NULL UNIQUE,
                    note TEXT,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                )
                """
            )
            cursor.execute(
                """
                INSERT INTO vault_samples (name, note)
                VALUES
                    ('Gold Ring', 'Sample row for connectivity check'),
                    ('Silver Necklace', 'Second sample row')
                ON CONFLICT (name) DO NOTHING
                """
            )
            inserted = cursor.rowcount
        return JsonResponse({"status": "ok", "inserted": inserted})
    except Exception as exc:  # pragma: no cover - defensive logging surface
        return JsonResponse({"error": str(exc)}, status=500)
