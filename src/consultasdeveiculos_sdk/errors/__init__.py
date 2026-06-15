"""Módulo de erros da SDK."""

from consultasdeveiculos_sdk.errors.sdk_error import (
    SDKError,
    AuthenticationError,
    ValidationError,
    RateLimitError,
    EndpointNotFoundError,
    SpecificationError,
)

__all__ = [
    "SDKError",
    "AuthenticationError",
    "ValidationError",
    "RateLimitError",
    "EndpointNotFoundError",
    "SpecificationError",
]
