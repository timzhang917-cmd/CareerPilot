import logging

from django.conf import settings
from django.db import DatabaseError
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST
from openai import OpenAIError

from analyses.models import Analysis

from .services import answer_question, save_exchange

logger = logging.getLogger(__name__)

MAX_QUESTION_LENGTH = 500
SHOWN_HISTORY_LIMIT = 50


def login_required_json():
    # JSON instead of a login redirect, because the chat box reads this response
    return JsonResponse({"error": "Please log in to use the assistant."}, status=401)


def analysis_not_found():
    return JsonResponse({"error": "This analysis could not be found."}, status=404)


def get_user_analysis(user, analysis_id):
    # analysis_id comes from the browser: only ever read the user's own analyses
    return (
        Analysis.objects
        .select_related("user", "resume", "job_description")
        .filter(id=analysis_id, user=user)
        .first()
    )


@require_POST
def chat(request):
    if not request.user.is_authenticated:
        return login_required_json()

    question = request.POST.get("question", "").strip()

    if not question:
        return JsonResponse({"error": "Please enter a question."}, status=400)

    if len(question) > MAX_QUESTION_LENGTH:
        return JsonResponse(
            {"error": f"Please keep your question under {MAX_QUESTION_LENGTH} characters."},
            status=400,
        )

    analysis = None
    analysis_id = request.POST.get("analysis_id", "")

    if analysis_id:
        if not analysis_id.isdecimal():
            return analysis_not_found()

        analysis = get_user_analysis(request.user, analysis_id)

        if analysis is None:
            return analysis_not_found()

    try:
        if analysis is None:
            result = answer_question(question)
        else:
            result = answer_question(question, analysis=analysis)
            save_exchange(analysis, question, result["answer"])
    except (OpenAIError, DatabaseError, ValueError, KeyError, TypeError):
        logger.exception("The assistant could not answer a question.")
        return JsonResponse(
            {"error": "The assistant is unavailable right now. Please try again later."},
            status=503,
        )

    sources = [source["title"] for source in result["sources"]]

    if result.get("used_analysis"):
        sources.insert(0, "This analysis")

    data = {
        "answer": result["answer"],
        "sources": sources,
    }

    if settings.DEBUG:  # shows the retrieval step in the chat box during development
        data["retrieved"] = [
            {
                "id": chunk["id"],
                "title": chunk["title"],
                "similarity": round(chunk["similarity"], 3),
            }
            for chunk in result["retrieved"]
        ]

    return JsonResponse(data)


@require_GET
def history(request, analysis_id):
    if not request.user.is_authenticated:
        return login_required_json()

    analysis = get_user_analysis(request.user, analysis_id)

    if analysis is None:
        return analysis_not_found()

    messages = analysis.chat_messages.order_by("-created_at", "-id")[:SHOWN_HISTORY_LIMIT]

    return JsonResponse(
        {
            "messages": [
                {"role": message.role, "content": message.content}
                for message in reversed(messages)
            ],
        }
    )
