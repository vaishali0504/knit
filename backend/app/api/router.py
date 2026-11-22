from fastapi import APIRouter
from app.api import health, auth, emails, ai, tasks, assistant, analytics, connections

api_router = APIRouter()

# Include health check
api_router.include_router(health.router, tags=["Health"])

# Include authentication
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])

# Include sample email management
api_router.include_router(emails.router, prefix="/emails", tags=["Sample Emails"])

# Include AI email intelligence
api_router.include_router(ai.router, prefix="/ai", tags=["AI Email Intelligence"])

# Include task and deadline management
api_router.include_router(tasks.router, prefix="/tasks", tags=["Tasks"])

# Include AI assistant conversations
api_router.include_router(assistant.router, prefix="/assistant", tags=["AI Assistant"])

# Include user-scoped dashboard analytics
api_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])

# Gmail account connection lifecycle
api_router.include_router(connections.router, prefix="/connections", tags=["Connected Accounts"])
