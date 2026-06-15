"""Parser de requisições Postman."""

import json
import unicodedata
import re


class RequestParser:
    """Converte um item de requisição do Postman em uma definição de endpoint."""

    def parse(self, item: dict, namespace: str = "") -> dict | None:
        """Parseia um item de requisição do Postman."""
        request = item.get("request")
        if not request:
            return None

        name = item.get("name", "Unnamed")
        method_name = self._normalize_method_name(name)
        key = f"{namespace}.{method_name}" if namespace else method_name

        return {
            "key": key,
            "name": name,
            "namespace": namespace,
            "method": self._parse_method(request),
            "url": self._parse_url(request),
            "headers": self._parse_headers(request),
            "body": self._parse_body(request),
            "auth": self._parse_auth(request),
            "description": self._parse_description(request),
            "responses": self._parse_responses(item),
            "variables": self._parse_variables(request),
            "raw": item,
        }

    def _normalize_method_name(self, name: str) -> str:
        """Normaliza o nome do método."""
        cleaned = re.sub(r"[^\w\s]", "", name)
        words = cleaned.split()
        result = []
        for i, word in enumerate(words):
            if i == 0:
                result.append(word.lower())
            else:
                result.append(word.capitalize())
        return "".join(result)

    def _parse_method(self, request) -> str:
        """Extrai o método HTTP."""
        if isinstance(request, str):
            return "GET"
        return request.get("method", "GET")

    def _parse_url(self, request) -> str:
        """Extrai a URL."""
        if isinstance(request, str):
            return request

        url = request.get("url")
        if not url:
            return ""
        if isinstance(url, str):
            return url
        if url.get("raw"):
            return url["raw"]

        protocol = url.get("protocol", "https")
        host = ".".join(url["host"]) if isinstance(url.get("host"), list) else (url.get("host", ""))
        path = "/".join(url["path"]) if isinstance(url.get("path"), list) else (url.get("path", ""))
        port = f":{url['port']}" if url.get("port") else ""

        return f"{protocol}://{host}{port}/{path}"

    def _parse_headers(self, request) -> dict:
        """Extrai headers."""
        headers = {}
        if isinstance(request, str) or "header" not in request:
            return headers

        for header in (request.get("header") or []):
            if header.get("disabled"):
                continue
            key = header.get("key", "")
            if not key or not isinstance(key, str) or not key.strip():
                continue
            headers[key] = header.get("value", "")
        return headers

    def _parse_body(self, request) -> dict | str | None:
        """Extrai body."""
        if isinstance(request, str) or "body" not in request:
            return None

        body = request["body"]
        mode = body.get("mode")

        if mode == "raw":
            return self._parse_raw_body(body)
        elif mode == "urlencoded":
            return self._parse_urlencoded_body(body)
        elif mode == "formdata":
            return self._parse_formdata_body(body)
        elif mode == "graphql":
            return self._parse_graphql_body(body)
        return None

    def _parse_raw_body(self, body: dict):
        """Parseia body raw (geralmente JSON)."""
        raw = body.get("raw", "")
        try:
            return json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            return raw

    def _parse_urlencoded_body(self, body: dict) -> dict:
        """Parseia body urlencoded."""
        result = {}
        for item in (body.get("urlencoded") or []):
            if item.get("disabled"):
                continue
            result[item["key"]] = item.get("value", "")
        return result

    def _parse_formdata_body(self, body: dict) -> dict:
        """Parseia body formdata."""
        result = {}
        for item in (body.get("formdata") or []):
            if item.get("disabled"):
                continue
            if item.get("type") == "file":
                result[item["key"]] = f"[FILE: {item.get('src', '')}]"
            else:
                result[item["key"]] = item.get("value", "")
        return result

    def _parse_graphql_body(self, body: dict) -> dict:
        """Parseia body GraphQL."""
        graphql = body.get("graphql", {})
        return {"query": graphql.get("query"), "variables": graphql.get("variables")}

    def _parse_auth(self, request) -> dict | None:
        """Extrai configuração de autenticação."""
        if isinstance(request, str) or "auth" not in request:
            return None
        auth = request["auth"]
        return {"type": auth.get("type"), "configured": True}

    def _parse_description(self, request) -> str:
        """Extrai descrição."""
        if isinstance(request, str):
            return ""
        desc = request.get("description", "")
        if not desc:
            return ""
        if isinstance(desc, dict):
            return desc.get("content", "")
        return str(desc)

    def _parse_responses(self, item: dict) -> list:
        """Extrai respostas de exemplo."""
        responses = []
        for resp in (item.get("response") or []):
            parsed = {
                "name": resp.get("name", ""),
                "status": resp.get("code") or resp.get("status", 200),
                "headers": {},
                "body": None,
            }
            for h in (resp.get("header") or []):
                if h.get("key"):
                    parsed["headers"][h["key"]] = h.get("value", "")

            body_str = resp.get("body")
            if body_str:
                try:
                    parsed["body"] = json.loads(body_str)
                except (json.JSONDecodeError, TypeError):
                    parsed["body"] = body_str

            responses.append(parsed)
        return responses

    def _parse_variables(self, request) -> list:
        """Extrai variáveis do request."""
        if isinstance(request, str):
            return []
        url = request.get("url")
        if not url or isinstance(url, str):
            return []
        return url.get("variable", [])
