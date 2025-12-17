from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_GET

from backend.firebase.firebase import db


@require_GET
def ping_view(request):
    return JsonResponse({"status": "ok"})


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


def root_message(request):
    return HttpResponse("Up and running boss!")
