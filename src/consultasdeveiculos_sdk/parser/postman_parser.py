"""Parser principal de coleções Postman."""

import re

from consultasdeveiculos_sdk.parser.folder_parser import FolderParser
from consultasdeveiculos_sdk.parser.request_parser import RequestParser


class PostmanParser:
    """Converte uma coleção Postman completa em endpoints utilizáveis pela SDK."""

    def __init__(self):
        self.folder_parser = FolderParser()
        self.request_parser = RequestParser()

    def parse(self, collection: dict) -> list[dict]:
        """Parseia uma coleção Postman completa."""
        if not collection or "item" not in collection:
            return []

        endpoints = []
        for item in collection["item"]:
            if self._is_folder(item):
                folder_endpoints = self.folder_parser.parse(item, "")
                endpoints.extend(folder_endpoints)
            elif self._is_request(item):
                endpoint = self.request_parser.parse(item, "")
                if endpoint:
                    endpoints.append(endpoint)

        return self._post_process(endpoints, collection)

    def _is_folder(self, item: dict) -> bool:
        return isinstance(item.get("item"), list) and len(item["item"]) > 0

    def _is_request(self, item: dict) -> bool:
        return "request" in item

    def _post_process(self, endpoints: list[dict], collection: dict) -> list[dict]:
        """Pós-processamento dos endpoints."""
        variables = self._extract_variables(collection)

        for endpoint in endpoints:
            endpoint["url"] = self._replace_variables(endpoint.get("url", ""), variables)
            for key, value in endpoint.get("headers", {}).items():
                endpoint["headers"][key] = self._replace_variables(value, variables)
            endpoint["collection_name"] = collection.get("info", {}).get("name")

        return endpoints

    def _extract_variables(self, collection: dict) -> dict:
        """Extrai variáveis da coleção."""
        variables = {}
        for v in (collection.get("variable") or []):
            if v.get("key"):
                variables[v["key"]] = v.get("value", "")
        return variables

    def _replace_variables(self, text, variables: dict) -> str:
        """Substitui variáveis Postman ({{var}})."""
        if not isinstance(text, str):
            return text or ""

        def replacer(match):
            key = match.group(1)
            return variables.get(key, match.group(0))

        return re.sub(r"\{\{(\w+)\}\}", replacer, text)
