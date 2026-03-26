from fastapi import Request
from fastapi.responses import JSONResponse
import logging
import traceback

logger = logging.getLogger(__name__)

async def error_handler(request: Request, exc: Exception):
    """Global error handler for all exceptions."""
    error_id = id(exc)
    
    logger.error(
        f"Error {error_id}: {str(exc)}\n"
        f"Path: {request.url.path}\n"
        f"Method: {request.method}\n"
        f"Traceback: {traceback.format_exc()}"
    )
    
    # Avoid leaking internal exception details in API responses.
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "error_id": error_id,
            "message": "Something went wrong. Please try again."
        }
    )
