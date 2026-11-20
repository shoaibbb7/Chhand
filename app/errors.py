from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


class ChhandAppError(Exception):
    """Base exception for application errors."""

    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        details: dict[str, Any] | None = None,
    ):
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details or {}


class InvalidMeterError(ChhandAppError):
    def __init__(
        self,
        message: str = "Invalid or unsupported meter specified.",
        details: dict[str, Any] | None = None,
    ):
        super().__init__(
            code="INVALID_METER",
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            details=details,
        )


class InvalidMeterRequestError(ChhandAppError):
    def __init__(
        self,
        message: str = "Invalid meter or charan target specified.",
        details: dict[str, Any] | None = None,
    ):
        super().__init__(
            code="INVALID_METER_REQUEST",
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            details=details,
        )


class InvalidInputError(ChhandAppError):
    def __init__(
        self,
        message: str = "Input contains invalid or malformed data.",
        details: dict[str, Any] | None = None,
    ):
        super().__init__(
            code="INVALID_INPUT",
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            details=details,
        )


class InvalidCustomPatternError(ChhandAppError):
    def __init__(
        self,
        message: str = "Custom pattern must be a list of positive integers.",
        details: dict[str, Any] | None = None,
    ):
        super().__init__(
            code="INVALID_CUSTOM_PATTERN",
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            details=details,
        )


class GeminiNotConfiguredError(ChhandAppError):
    def __init__(
        self,
        message: str = "AI suggestions are currently unavailable. Meter analysis and rhyme search are still available.",
        details: dict[str, Any] | None = None,
    ):
        super().__init__(
            code="GEMINI_NOT_CONFIGURED",
            message=message,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            details=details,
        )


class GeminiAuthError(ChhandAppError):
    def __init__(
        self,
        message: str = "Authentication failed with the Gemini API.",
        details: dict[str, Any] | None = None,
    ):
        super().__init__(
            code="GEMINI_AUTH_ERROR",
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            details=details,
        )


class GeminiRateLimitError(ChhandAppError):
    def __init__(
        self,
        message: str = "Gemini API rate limit exceeded. Please wait a moment and try again.",
        details: dict[str, Any] | None = None,
    ):
        super().__init__(
            code="GEMINI_RATE_LIMIT",
            message=message,
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            details=details,
        )


class GeminiTimeoutError(ChhandAppError):
    def __init__(
        self,
        message: str = "Gemini API request timed out.",
        details: dict[str, Any] | None = None,
    ):
        super().__init__(
            code="GEMINI_TIMEOUT",
            message=message,
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            details=details,
        )


class GeminiProviderError(ChhandAppError):
    def __init__(
        self,
        message: str = "Error returned from Gemini API provider.",
        details: dict[str, Any] | None = None,
    ):
        super().__init__(
            code="GEMINI_PROVIDER_ERROR",
            message=message,
            status_code=status.HTTP_502_BAD_GATEWAY,
            details=details,
        )


class GeminiInvalidResponseError(ChhandAppError):
    def __init__(
        self,
        message: str = "Gemini returned a response that could not be parsed into the expected schema.",
        details: dict[str, Any] | None = None,
    ):
        super().__init__(
            code="GEMINI_INVALID_RESPONSE",
            message=message,
            status_code=status.HTTP_502_BAD_GATEWAY,
            details=details,
        )


# Backward-compatible aliases
LLMConfigurationError = GeminiNotConfiguredError
GeminiConfigurationError = GeminiNotConfiguredError
LLMTimeoutError = GeminiTimeoutError
LLMProviderError = GeminiProviderError


class NoVerifiedRewritesError(ChhandAppError):
    def __init__(
        self,
        message: str = "No candidates passed deterministic meter verification.",
        details: dict[str, Any] | None = None,
    ):
        super().__init__(
            code="NO_VERIFIED_SUGGESTIONS",
            message=message,
            status_code=status.HTTP_200_OK,
            details=details,
        )


def register_error_handlers(app: FastAPI) -> None:
    """Registers standard JSON exception handlers on the FastAPI app."""

    @app.exception_handler(ChhandAppError)
    async def chhand_app_error_handler(_request: Request, exc: ChhandAppError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                    "details": exc.details,
                }
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(
        _request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Request payload failed schema validation.",
                    "details": exc.errors(),
                }
            },
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(_request: Request, exc: Exception) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": "An unexpected error occurred. Please try again later.",
                    "details": {"type": type(exc).__name__},
                }
            },
        )
