"""Registro de endpoints da SDK."""

from __future__ import annotations

import re
from consultasdeveiculos_sdk.errors import EndpointNotFoundError


class EndpointRegistry:
    """Armazena e gerencia todos os endpoints parseados da coleção Postman."""

    def __init__(self):
        self.endpoints: dict[str, dict] = {}
        self.namespace_tree: dict = {}

    def register(self, endpoint: dict):
        """Registra um endpoint."""
        key = endpoint.get("key")
        if not key:
            raise ValueError("Endpoint deve ter uma key")
        self.endpoints[key] = endpoint
        self._add_to_namespace_tree(key, endpoint)

    def get(self, key: str) -> dict:
        """Obtém um endpoint pelo key."""
        endpoint = self.endpoints.get(key)
        if not endpoint:
            raise EndpointNotFoundError(f'Endpoint "{key}" não encontrado', {"key": key})
        return endpoint

    def has(self, key: str) -> bool:
        """Verifica se um endpoint existe."""
        return key in self.endpoints

    def list(self) -> list[dict]:
        """Lista todos os endpoints."""
        return list(self.endpoints.values())

    def list_by_namespace(self, namespace: str) -> list[dict]:
        """Lista endpoints por namespace."""
        return [ep for ep in self.endpoints.values() if ep["key"].startswith(namespace + ".")]

    def get_namespace_tree(self) -> dict:
        """Obtém a árvore de namespaces."""
        return self.namespace_tree

    def get_namespaces(self) -> list[str]:
        """Obtém todos os namespaces de primeiro nível."""
        return list(self.namespace_tree.keys())

    def clear(self):
        """Limpa o registro."""
        self.endpoints.clear()
        self.namespace_tree.clear()

    @property
    def size(self) -> int:
        """Quantidade de endpoints registrados."""
        return len(self.endpoints)

    def search(self, pattern: str) -> list[dict]:
        """Busca endpoints por padrão."""
        regex = re.compile(pattern, re.IGNORECASE)
        return [
            ep for ep in self.endpoints.values()
            if regex.search(ep.get("key", ""))
            or regex.search(ep.get("name", ""))
            or regex.search(ep.get("description", "") or "")
        ]

    def _add_to_namespace_tree(self, key: str, endpoint: dict):
        """Adiciona endpoint à árvore de namespaces."""
        parts = key.split(".")
        current = self.namespace_tree

        for part in parts[:-1]:
            if part not in current:
                current[part] = {"_methods": {}}
            current = current[part]

        method_name = parts[-1]
        if "_methods" not in current:
            current["_methods"] = {}
        current["_methods"][method_name] = endpoint
