"""Transporte HTTP usando requests."""

import time
import requests as req

from consultasdeveiculos_sdk.transport.transport import Transport
from consultasdeveiculos_sdk.errors import (
    SDKError,
    AuthenticationError,
    ValidationError,
    RateLimitError,
)


class HttpTransport(Transport):
    """Responsável por chamadas HTTP reais."""

    def __init__(self, options: dict | None = None):
        super().__init__(options)
        self.session = req.Session()

    def request(self, endpoint: dict, params: dict | None = None, options: dict | None = None) -> dict:
        """Executa uma requisição HTTP."""
        params = params or {}
        options = options or {}

        url = self.build_url(endpoint, params)
        headers = self.build_headers(endpoint, params)
        body = self.build_body(endpoint, params)
        method = (endpoint.get("method") or "GET").upper()

        # Adiciona auth_token no body
        if self.token and body and isinstance(body, dict):
            body = {"auth_token": self.token, **body}
            if body.get("auth_token") == "{{api_token}}":
                body["auth_token"] = self.token

        timeout_ms = options.get("timeout", self.timeout)
        timeout_s = timeout_ms / 1000

        return self._execute_with_retry(method, url, headers, body, timeout_s, options)

    def _execute_with_retry(self, method: str, url: str, headers: dict, body: dict | None, timeout: float, options: dict) -> dict:
        """Executa requisição com retry exponencial."""
        max_retries = options.get("max_retries", self.max_retries)
        last_error = None

        for attempt in range(max_retries + 1):
            try:
                kwargs = {
                    "method": method,
                    "url": url,
                    "headers": headers,
                    "timeout": timeout,
                }

                if body and method in ("POST", "PUT", "PATCH", "DELETE"):
                    kwargs["json"] = body

                response = self.session.request(**kwargs)
                return self._handle_response(response)

            except (AuthenticationError, ValidationError):
                raise
            except RateLimitError as e:
                if e.retry_after:
                    time.sleep(e.retry_after)
                    continue
                raise
            except Exception as e:
                last_error = e
                if attempt == max_retries:
                    break
                delay = (self.retry_delay / 1000) * (2 ** attempt)
                time.sleep(delay)

        if last_error:
            raise last_error
        raise SDKError("Falha na requisição após múltiplas tentativas")

    def _handle_response(self, response: req.Response) -> dict:
        """Processa a resposta HTTP."""
        content_type = response.headers.get("content-type", "")

        if "application/json" in content_type:
            try:
                data = response.json()
            except Exception:
                data = response.text
        else:
            data = response.text

        if response.ok:
            return {
                "success": True,
                "status": response.status_code,
                "data": data,
                "headers": dict(response.headers),
            }

        status = response.status_code
        message = data.get("message", "") if isinstance(data, dict) else ""

        if status in (401, 403):
            raise AuthenticationError(
                message or "Token inválido ou expirado",
                {"status": status, "data": data},
            )
        elif status in (400, 422):
            raise ValidationError(
                message or "Dados inválidos",
                {"status": status, "errors": data.get("errors") if isinstance(data, dict) else None, "data": data},
            )
        elif status == 429:
            retry_after = int(response.headers.get("retry-after", 60))
            raise RateLimitError(
                message or "Limite de requisições excedido",
                {"status": status, "retryAfter": retry_after, "data": data},
            )
        elif status == 404:
            raise SDKError(message or "Recurso não encontrado", "NOT_FOUND", {"status": status, "data": data})
        elif status >= 500:
            raise SDKError(message or "Erro interno do servidor", "SERVER_ERROR", {"status": status, "data": data})
        else:
            raise SDKError(message or f"Erro HTTP {status}", "HTTP_ERROR", {"status": status, "data": data})
