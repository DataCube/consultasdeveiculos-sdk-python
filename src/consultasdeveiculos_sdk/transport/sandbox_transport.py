"""Transporte Sandbox - retorna dados simulados sem chamar a API."""

import time
import random
import re
import json

from consultasdeveiculos_sdk.transport.transport import Transport
from consultasdeveiculos_sdk.errors import SDKError


class SandboxTransport(Transport):
    """Retorna exemplos presentes no Postman. Não faz chamadas externas."""

    def __init__(self, options: dict | None = None):
        super().__init__(options)
        options = options or {}
        self.delay = options.get("sandbox_delay", 0.1)
        self.random_errors = options.get("sandbox_random_errors", False)
        self.error_rate = options.get("sandbox_error_rate", 0.1)

    def request(self, endpoint: dict, params: dict | None = None, options: dict | None = None) -> dict:
        """Retorna exemplo de resposta do Postman."""
        params = params or {}

        # Simula latência de rede
        self._simulate_delay()

        # Simula erros aleatórios se habilitado
        if self.random_errors and random.random() < self.error_rate:
            raise SDKError(
                "Erro simulado de sandbox",
                "SANDBOX_SIMULATED_ERROR",
                {"endpoint": endpoint.get("key")},
            )

        response = self._find_example_response(endpoint, params)

        return {
            "success": True,
            "status": response.get("status", 200),
            "data": response.get("data"),
            "headers": response.get("headers", {}),
            "sandbox": True,
            "endpoint": endpoint.get("key"),
        }

    def _find_example_response(self, endpoint: dict, params: dict) -> dict:
        """Encontra a resposta de exemplo mais adequada."""
        responses = endpoint.get("responses") or []

        if not responses:
            return {
                "status": 200,
                "data": {
                    "success": True,
                    "message": f"Sandbox response for {endpoint.get('name', '')}",
                    "endpoint": endpoint.get("key"),
                    "params": self._sanitize_params(params),
                },
            }

        # Tenta encontrar resposta de sucesso (2xx)
        success_response = next(
            (r for r in responses if 200 <= (r.get("status") or 200) < 300),
            None,
        )

        if success_response:
            return self._process_response(success_response, params)

        return self._process_response(responses[0], params)

    def _process_response(self, response: dict, params: dict) -> dict:
        """Processa a resposta, substituindo placeholders."""
        data = response.get("body") or response.get("data")

        if isinstance(data, str):
            try:
                data = json.loads(data)
            except (json.JSONDecodeError, TypeError):
                pass

        data = self._replace_placeholders(data, params)

        return {
            "status": response.get("status") or response.get("code") or 200,
            "data": data,
            "headers": response.get("headers", {}),
        }

    def _replace_placeholders(self, data, params: dict):
        """Substitui placeholders como {{param}} nos dados."""
        if isinstance(data, str):
            return self._replace_in_string(data, params)
        if isinstance(data, list):
            return [self._replace_placeholders(item, params) for item in data]
        if isinstance(data, dict):
            return {k: self._replace_placeholders(v, params) for k, v in data.items()}
        return data

    def _replace_in_string(self, text: str, params: dict) -> str:
        """Substitui placeholders em uma string."""
        all_params = {
            **(params.get("path") or {}),
            **(params.get("query") or {}),
            **(params.get("body") or params),
        }

        def replacer(match):
            key = match.group(1)
            return str(all_params[key]) if key in all_params else match.group(0)

        return re.sub(r"\{\{(\w+)\}\}", replacer, text)

    def _sanitize_params(self, params: dict) -> dict:
        """Remove informações sensíveis dos params."""
        sanitized = dict(params)
        if "headers" in sanitized:
            headers = dict(sanitized["headers"])
            headers.pop("Authorization", None)
            headers.pop("authorization", None)
            sanitized["headers"] = headers
        return sanitized

    def _simulate_delay(self):
        """Simula delay de rede."""
        jitter = random.random() * self.delay * 0.5
        time.sleep(self.delay + jitter)
