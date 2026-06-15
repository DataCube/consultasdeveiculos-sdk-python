"""Interface base para transporte de requisições."""

import re
from urllib.parse import urlencode, quote


class Transport:
    """Define o contrato que todos os transportes devem seguir."""

    def __init__(self, options: dict | None = None):
        options = options or {}
        self.token = options.get("token")
        self.base_url = options.get("base_url")
        self.timeout = options.get("timeout", 30000)
        self.max_retries = options.get("max_retries", 3)
        self.retry_delay = options.get("retry_delay", 1000)
        self.headers = options.get("headers", {})

    def request(self, endpoint: dict, params: dict | None = None, options: dict | None = None) -> dict:
        """Executa uma requisição."""
        raise NotImplementedError("Método request() deve ser implementado")

    def build_url(self, endpoint: dict, params: dict | None = None) -> str:
        """Constrói a URL final com path parameters."""
        params = params or {}
        url = endpoint.get("url", "")
        path_params = params.get("path", {})

        for key, value in path_params.items():
            url = url.replace(f"{{{{{key}}}}}", quote(str(value)))
            url = re.sub(rf":{key}(?=/|$)", quote(str(value)), url)

        query_params = params.get("query", {})
        if query_params:
            filtered = {k: v for k, v in query_params.items() if v is not None}
            if filtered:
                separator = "&" if "?" in url else "?"
                url += separator + urlencode(filtered)

        if self.base_url and not url.startswith("http"):
            url = self.base_url.rstrip("/") + "/" + url.lstrip("/")

        return url

    def build_headers(self, endpoint: dict, params: dict | None = None) -> dict:
        """Mescla headers."""
        params = params or {}
        return {
            **self.headers,
            **(endpoint.get("headers") or {}),
            **(params.get("headers") or {}),
        }

    def build_body(self, endpoint: dict, params: dict | None = None) -> dict | None:
        """Constrói o body da requisição."""
        params = params or {}
        body = params.get("body", params)

        # Remove propriedades especiais que não são body
        body_data = {k: v for k, v in body.items() if k not in ("path", "query", "headers")}

        # Se tem template de body no endpoint, faz merge
        if endpoint.get("body") and isinstance(endpoint["body"], dict):
            return {**endpoint["body"], **body_data}

        return body_data if body_data else None
