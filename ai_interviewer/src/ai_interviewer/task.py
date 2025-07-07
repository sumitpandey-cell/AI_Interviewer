# DEPRECATED: This task used the old LangGraph system
# All interview processing now uses the workflow system

from celery import shared_task

@shared_task
def process_interview_async(session_data):
    """DEPRECATED: Use the workflow system instead."""
    raise DeprecationWarning(
        "This task is deprecated. Use the workflow system for interview processing."
    )
