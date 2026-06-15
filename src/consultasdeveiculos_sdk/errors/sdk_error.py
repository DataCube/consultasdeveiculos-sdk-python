"""Classes de erro da SDK."""

from datetime import datetime, timezone


class SDKError(Exception):
    """Classe base para todos os erros da SDK."""

    def __init__(self, message: str, code: str = "SDK_ERROR", details: dict | None = None):
        super().__init__(message)
        self.error_code = code
        self.details = self._sanitize_details(details)
        self.timestamp = datetime.now(timezone.utc).isoformat()

    def _sanitize_details(self, details: dict | None) -> dict | None:
        """Remove dados sensíveis dos detalhes do erro."""
        if not details or not isinstance(details, dict):
            return details

        sensitive_keys = ["auth_token", "token", "password", "secret", "api_key", "apikey", "authorization"]
        sanitized = dict(details)

        def sanitize_obj(obj):
            if not isinstance(obj, dict):
                return obj
            for key in list(obj.keys()):
                lower_key = key.lower()
                if any(sk in lower_key for sk in sensitive_keys):
                    obj[key] = "[REDACTED]"
                elif isinstance(obj[key], dict):
                    sanitize_obj(obj[key])
            return obj

        return sanitize_obj(sanitized)

    def to_dict(self) -> dict:
        """Serializa erro para dict (sem stack trace por segurança)."""
        return {
            "name": self.__class__.__name__,
            "message": str(self),
            "code": self.error_code,
            "details": self.details,
            "timestamp": self.timestamp,
        }

    def to_json(self) -> str:
        """Serializa erro para JSON."""
        import json
        return json.dumps(self.to_dict(), ensure_ascii=False)


class AuthenticationError(SDKError):
    """Erro de autenticação."""

    def __init__(self, message: str = "Falha na autenticação", details: dict | None = None):
        super().__init__(message, "AUTHENTICATION_ERROR", details)


class ValidationError(SDKError):
    """Erro de validação."""

    def __init__(self, message: str = "Erro de validação", details: dict | None = None):
        super().__init__(message, "VALIDATION_ERROR", details)


class RateLimitError(SDKError):
    """Erro de rate limiting."""

    def __init__(self, message: str = "Limite de requisições excedido", details: dict | None = None):
        super().__init__(message, "RATE_LIMIT_ERROR", details)
        self.retry_after = details.get("retryAfter") if details else None


class EndpointNotFoundError(SDKError):
    """Erro de endpoint não encontrado."""

    def __init__(self, message: str = "Endpoint não encontrado", details: dict | None = None):
        super().__init__(message, "ENDPOINT_NOT_FOUND", details)


class SpecificationError(SDKError):
    """Erro de especificação."""

    def __init__(self, message: str = "Erro na especificação da API", details: dict | None = None):
        super().__init__(message, "SPECIFICATION_ERROR", details)
