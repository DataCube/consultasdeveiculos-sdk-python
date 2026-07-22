"""ConsultadeveiculosSDK - Classe principal."""

import re
from urllib.parse import urlparse

from consultasdeveiculos_sdk.core.config_manager import ConfigManager
from consultasdeveiculos_sdk.core.postman_loader import PostmanLoader
from consultasdeveiculos_sdk.core.endpoint_registry import EndpointRegistry
from consultasdeveiculos_sdk.parser.postman_parser import PostmanParser
from consultasdeveiculos_sdk.transport.http_transport import HttpTransport
from consultasdeveiculos_sdk.transport.sandbox_transport import SandboxTransport
from consultasdeveiculos_sdk.errors import (
    AuthenticationError,
    EndpointNotFoundError,
    SpecificationError,
)


class ConsultadeveiculosSDK:
    """
    Runtime Engine que consome endpoints definidos em coleções Postman
    sem necessidade de implementação manual de cada endpoint.

    TODAS as funções são geradas dinamicamente via __getattr__.

    Exemplo:
        client = ConsultadeveiculosSDK(auth_token="TOKEN")
        result = client.veiculos_agregados(placa="ABC1234")

        # Modo sandbox
        client = ConsultadeveiculosSDK(sandbox=True)
    """

    VERSION = "1.0.1"

    def __init__(self, auth_token: str | None = None, sandbox: bool = False, **options):
        self.sandbox = sandbox
        self.options = options
        self._auth_token = None if sandbox else auth_token

        # Validação do token em modo produção
        if not self.sandbox and not self._auth_token:
            raise AuthenticationError(
                "auth_token é obrigatório. Use sandbox=True para modo de teste."
            )

        self._slug_map: dict[str, dict] = {}
        self._initialized = False
        self._init_sync()

    def _init_sync(self):
        """Inicialização síncrona da SDK."""
        # 1. Carrega configuração
        self.config_manager = ConfigManager(self.options)

        # 2. Carrega Manifest e Postman
        loader = PostmanLoader(self.config_manager)
        result = loader.load()
        self.manifest = result["manifest"]
        self.postman = result["postman"]

        # 3. Valida compatibilidade
        self._validate_compatibility()

        # 4. Cria registro de endpoints
        self.registry = EndpointRegistry()

        # 5. Parseia a coleção Postman
        parser = PostmanParser()
        endpoints = parser.parse(self.postman)

        # 6. Registra endpoints e cria mapa de slugs
        for endpoint in endpoints:
            self.registry.register(endpoint)
            slug = self._url_to_slug(endpoint.get("url", ""))
            if slug:
                self._slug_map[slug] = endpoint

        # 7. Cria transport
        self.transport = self._create_transport()
        self._initialized = True

    def _url_to_slug(self, url: str) -> str | None:
        """Converte URL em slug para nome do método."""
        if not url:
            return None

        try:
            path = url
            if "://" in url:
                parsed = urlparse(url)
                path = parsed.path

            # Remove barra inicial e final
            path = path.strip("/")
            # Remove variáveis de path como {{baseUrl}}
            path = re.sub(r"\{\{[^}]+\}\}", "", path).lstrip("/")
            # Substitui / por _ e - por _
            slug = path.replace("/", "_").replace("-", "_")
            slug = re.sub(r"_+", "_", slug)  # Remove underscores duplicados
            slug = slug.strip("_").lower()
            return slug or None
        except Exception:
            return None

    def _validate_compatibility(self):
        """Valida compatibilidade entre Runtime e Specification."""
        min_version = self.manifest.get("minRuntimeVersion", "1.0.0")
        if not self._is_version_compatible(self.VERSION, min_version):
            raise SpecificationError(
                f"Atualize a SDK para continuar. "
                f"Runtime atual: {self.VERSION}, Mínimo requerido: {min_version}"
            )

    def _is_version_compatible(self, current: str, minimum: str) -> bool:
        """Verifica se a versão é compatível (semver básico)."""
        def parse_ver(v):
            return [int(x) for x in v.split(".")]

        curr = parse_ver(current)
        mini = parse_ver(minimum)

        for c, m in zip(curr, mini):
            if c > m:
                return True
            if c < m:
                return False
        return True

    def _create_transport(self):
        """Cria o transport apropriado."""
        transport_options = {
            "token": self._auth_token,
            "base_url": self.options.get("base_url"),
            "timeout": self.config_manager.get("timeout"),
            "max_retries": self.config_manager.get("max_retries"),
            "retry_delay": self.config_manager.get("retry_delay"),
            "headers": {
                **self.config_manager.get("default_headers"),
                **(self.options.get("headers") or {}),
            },
        }

        if self.sandbox:
            return SandboxTransport(transport_options)
        return HttpTransport(transport_options)

    def __getattr__(self, name: str):
        """Intercepta chamadas de método e redireciona para o endpoint correto."""
        # Evita recursão infinita em atributos internos
        if name.startswith("_") or name in ("sandbox", "options", "config_manager", "manifest", "postman", "registry", "transport"):
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")

        if name in self._slug_map:
            def execute(**kwargs):
                return self.execute_by_slug(name, kwargs)
            return execute

        raise AttributeError(f"Endpoint '{name}' não encontrado. Use list_slugs() para ver os disponíveis.")

    def execute_by_slug(self, slug: str, params: dict | None = None) -> dict:
        """Executa um endpoint pelo slug."""
        params = params or {}
        endpoint = self._slug_map.get(slug)

        if not endpoint:
            available = list(self._slug_map.keys())[:5]
            raise EndpointNotFoundError(
                f'Endpoint "{slug}" não encontrado. Exemplos: {", ".join(available)}...',
                {"slug": slug, "available_examples": available},
            )

        return self.transport.request(endpoint, {"body": params})

    def has_endpoint(self, name: str) -> bool:
        """Verifica se um endpoint existe."""
        return name in self._slug_map

    def get_info(self) -> dict:
        """Obtém informações da SDK."""
        return {
            "runtimeVersion": self.VERSION,
            "specVersion": self.manifest.get("specVersion", ""),
            "generatedAt": self.manifest.get("generatedAt", ""),
            "sandbox": self.sandbox,
            "endpointsCount": self.registry.size,
            "namespaces": self.registry.get_namespaces(),
            "slugsCount": len(self._slug_map),
        }

    def list_endpoints(self) -> list[dict]:
        """Lista todos os endpoints disponíveis com seus slugs."""
        endpoints = []
        for slug, endpoint in self._slug_map.items():
            endpoints.append({
                "slug": slug,
                "key": endpoint.get("key", ""),
                "name": endpoint.get("name", ""),
                "method": endpoint.get("method", "GET"),
                "url": endpoint.get("url", ""),
                "description": endpoint.get("description", ""),
                "body": endpoint.get("body") or {},
            })
        return endpoints

    def _list_endpoints(self) -> list[dict]:
        """Método interno de inspeção dos endpoints."""
        return self.list_endpoints()

    def _listEndpoints(self) -> list[dict]:
        """Alias para _list_endpoints em camelCase."""
        return self.list_endpoints()

    def ListEndpoints(self) -> list[dict]:
        """Alias para list_endpoints em PascalCase."""
        return self.list_endpoints()

    def list_slugs(self) -> list[str]:
        """Lista apenas os slugs disponíveis."""
        return list(self._slug_map.keys())

    def _list_slugs(self) -> list[str]:
        """Método interno de inspeção dos slugs."""
        return self.list_slugs()

    def _listSlugs(self) -> list[str]:
        """Alias para _list_slugs em camelCase."""
        return self.list_slugs()

    def ListSlugs(self) -> list[str]:
        """Alias para list_slugs em PascalCase."""
        return self.list_slugs()

    def help(self, filter_term: str | None = None):
        """Exibe ajuda no console."""
        info = self.get_info()

        print()
        print("📦 ConsultadeveiculosSDK - Help")
        print("═" * 64)
        print()
        print(f"   Runtime: v{info['runtimeVersion']}")
        print(f"   Spec: v{info['specVersion']}")
        print(f"   Modo: {'🧪 SANDBOX' if info['sandbox'] else '🔴 PRODUÇÃO'}")
        print(f"   Endpoints: {info['endpointsCount']}")
        print(f"   Namespaces: {', '.join(info['namespaces'])}")
        print()
        print("─" * 64)
        print("📖 USO BÁSICO")
        print("─" * 64)
        print()
        print('   client = ConsultadeveiculosSDK(auth_token="SEU_TOKEN")')
        print('   result = client.SLUG(param="valor")')
        print()
        print("─" * 64)
        print("🔧 MÉTODOS AUXILIARES")
        print("─" * 64)
        print()
        print("   client.help()              Exibe esta ajuda")
        print('   client.help("veiculos")    Filtra endpoints por termo')
        print("   client.list_endpoints()    Lista todos os endpoints")
        print("   client.get_info()          Informações do SDK")
        print()

        if filter_term:
            print("─" * 64)
            print(f'🔍 ENDPOINTS COM "{filter_term.upper()}"')
            print("─" * 64)
            print()

            term = filter_term.lower()
            filtered = [
                ep for ep in self.list_endpoints()
                if term in ep["slug"].lower() or term in ep["name"].lower()
            ]
            if not filtered:
                print(f'   Nenhum endpoint encontrado para "{filter_term}"')
            else:
                for ep in filtered[:20]:
                    print(f"   📌 client.{ep['slug']}()")
                    print(f"      {ep['name']}")
                    print()
                if len(filtered) > 20:
                    print(f"   ... e mais {len(filtered) - 20} endpoints")

        print("═" * 64)
        print()
        return self

    def endpoints(self) -> list[dict]:
        """Lista todos os endpoints (imprime e retorna)."""
        ep_list = self.list_endpoints()

        print()
        print(f"📡 {len(ep_list)} Endpoints Disponíveis")
        print()

        grouped: dict[str, list] = {}
        for ep in ep_list:
            ns = ep["slug"].split("_")[0] if "_" in ep["slug"] else "outros"
            grouped.setdefault(ns, []).append(ep)

        for ns, eps in grouped.items():
            print(f"   {ns.upper()} ({len(eps)}):")
            for ep in eps[:5]:
                print(f"     • {ep['slug']}")
            if len(eps) > 5:
                print(f"     ... +{len(eps) - 5} mais")
            print()

        return ep_list

    def info(self) -> dict:
        """Exibe e retorna informações da SDK."""
        data = self.get_info()

        print()
        print("ℹ️  SDK Info")
        print()
        print(f"   Runtime: v{data['runtimeVersion']}")
        print(f"   Spec: v{data['specVersion']}")
        print(f"   Modo: {'Sandbox' if data['sandbox'] else 'Produção'}")
        print(f"   Endpoints: {data['endpointsCount']}")
        print(f"   Namespaces: {', '.join(data['namespaces'])}")
        print()

        return data


# Alias
SDK = ConsultadeveiculosSDK
