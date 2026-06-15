"""Parser de pastas Postman."""

import re
import unicodedata

from consultasdeveiculos_sdk.parser.request_parser import RequestParser


class FolderParser:
    """Parseia pastas/categorias do Postman e converte em namespaces."""

    def __init__(self):
        self.request_parser = RequestParser()

    def parse(self, folder: dict, parent_namespace: str = "") -> list[dict]:
        """Parseia uma pasta do Postman."""
        endpoints = []
        namespace = self._build_namespace(folder, parent_namespace)

        for item in (folder.get("item") or []):
            if self._is_folder(item):
                sub_endpoints = self.parse(item, namespace)
                endpoints.extend(sub_endpoints)
            elif self._is_request(item):
                endpoint = self.request_parser.parse(item, namespace)
                if endpoint:
                    endpoints.append(endpoint)

        return endpoints

    def _build_namespace(self, folder: dict, parent_namespace: str) -> str:
        """Constrói o namespace baseado no nome da pasta."""
        folder_name = folder.get("name", "")
        normalized = self._normalize_folder_name(folder_name)
        if not normalized:
            return parent_namespace
        return f"{parent_namespace}.{normalized}" if parent_namespace else normalized

    def _normalize_folder_name(self, name: str) -> str:
        """Normaliza o nome da pasta para namespace."""
        # Remove acentos
        nfkd = unicodedata.normalize("NFD", name)
        without_accents = "".join(c for c in nfkd if not unicodedata.combining(c))
        # Remove caracteres especiais
        cleaned = re.sub(r"[^\w\s]", "", without_accents)
        # Converte para camelCase
        words = cleaned.split()
        result = []
        for i, word in enumerate(words):
            if i == 0:
                result.append(word.lower())
            else:
                result.append(word.capitalize())
        return "".join(result)

    def _is_folder(self, item: dict) -> bool:
        return isinstance(item.get("item"), list) and len(item["item"]) > 0

    def _is_request(self, item: dict) -> bool:
        return "request" in item
