"""Testes da SDK."""

import pytest
from pathlib import Path
import sys

# Garante que o src está no path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from consultasdeveiculos_sdk import ConsultadeveiculosSDK, SDKError, AuthenticationError, EndpointNotFoundError


class TestSDKInit:
    """Testes de inicialização."""

    def test_deve_inicializar_em_modo_sandbox(self):
        sdk = ConsultadeveiculosSDK(sandbox=True)
        assert sdk.sandbox is True

    def test_deve_exigir_token_em_modo_producao(self):
        with pytest.raises(AuthenticationError):
            ConsultadeveiculosSDK()

    def test_deve_aceitar_token_em_modo_producao(self):
        sdk = ConsultadeveiculosSDK(auth_token="test-token")
        assert sdk.sandbox is False

    def test_deve_carregar_endpoints(self):
        sdk = ConsultadeveiculosSDK(sandbox=True)
        slugs = sdk.list_slugs()
        assert len(slugs) > 0

    def test_deve_ter_mais_de_100_endpoints(self):
        sdk = ConsultadeveiculosSDK(sandbox=True)
        info = sdk.get_info()
        assert info["slugsCount"] > 100


class TestSDKEndpoints:
    """Testes de endpoints."""

    def test_deve_listar_endpoints(self):
        sdk = ConsultadeveiculosSDK(sandbox=True)
        endpoints = sdk.list_endpoints()
        assert len(endpoints) > 0
        assert "slug" in endpoints[0]
        assert "name" in endpoints[0]

    def test_deve_verificar_existencia_de_endpoint(self):
        sdk = ConsultadeveiculosSDK(sandbox=True)
        slugs = sdk.list_slugs()
        assert sdk.has_endpoint(slugs[0]) is True
        assert sdk.has_endpoint("endpoint_inexistente_xyz") is False

    def test_deve_padronizar_listagem_de_endpoints_e_slugs(self):
        sdk = ConsultadeveiculosSDK(sandbox=True)
        endpoints = sdk.list_endpoints()
        slugs = sdk.list_slugs()

        assert len(endpoints) == len(slugs)
        for ep, slug in zip(endpoints, slugs):
            assert ep["slug"] == slug

        # Testa apelidos internos/privados e padrões de caixa (_listEndpoints, ListEndpoints, etc.)
        assert sdk._list_endpoints() == endpoints
        assert sdk._listEndpoints() == endpoints
        assert sdk.ListEndpoints() == endpoints

        assert sdk._list_slugs() == slugs
        assert sdk._listSlugs() == slugs
        assert sdk.ListSlugs() == slugs

    def test_nao_deve_possuir_metodo_search(self):
        sdk = ConsultadeveiculosSDK(sandbox=True)
        assert not hasattr(sdk, "search") or "search" not in dir(sdk)
        with pytest.raises(AttributeError):
            sdk.search("veiculos")

    def test_deve_retornar_info(self):
        sdk = ConsultadeveiculosSDK(sandbox=True)
        info = sdk.get_info()
        assert "runtimeVersion" in info
        assert "specVersion" in info
        assert "endpointsCount" in info
        assert info["sandbox"] is True

    def test_deve_listar_endpoints_do_registry(self):
        sdk = ConsultadeveiculosSDK(sandbox=True)
        assert sdk.registry.size > 0


class TestSDKExecution:
    """Testes de execução."""

    def test_deve_executar_endpoint_sandbox(self):
        sdk = ConsultadeveiculosSDK(sandbox=True)
        slugs = sdk.list_slugs()
        result = sdk.execute_by_slug(slugs[0], {"placa": "ABC1234"})
        assert result["sandbox"] is True

    def test_deve_executar_via_getattr(self):
        sdk = ConsultadeveiculosSDK(sandbox=True)
        slugs = sdk.list_slugs()
        first_slug = slugs[0]
        method = getattr(sdk, first_slug)
        result = method(placa="ABC1234")
        assert result["sandbox"] is True

    def test_deve_lancar_erro_endpoint_nao_encontrado(self):
        sdk = ConsultadeveiculosSDK(sandbox=True)
        with pytest.raises(EndpointNotFoundError):
            sdk.execute_by_slug("endpoint_que_nao_existe")

    def test_deve_lancar_attributeerror_para_slug_invalido(self):
        sdk = ConsultadeveiculosSDK(sandbox=True)
        with pytest.raises(AttributeError):
            sdk.endpoint_que_nao_existe()


class TestSDKErrors:
    """Testes de erros."""

    def test_sdk_error_deve_ter_code(self):
        err = SDKError("teste", "TEST_CODE", {"key": "value"})
        assert err.error_code == "TEST_CODE"
        assert err.details == {"key": "value"}

    def test_sdk_error_deve_sanitizar_token(self):
        err = SDKError("teste", "TEST", {"auth_token": "secret123"})
        assert err.details["auth_token"] == "[REDACTED]"

    def test_sdk_error_to_dict(self):
        err = SDKError("mensagem", "CODE", {"info": "data"})
        d = err.to_dict()
        assert d["message"] == "mensagem"
        assert d["code"] == "CODE"
        assert "timestamp" in d

    def test_authentication_error(self):
        err = AuthenticationError("token inválido")
        assert err.error_code == "AUTHENTICATION_ERROR"


class TestParser:
    """Testes do parser."""

    def test_deve_parsear_collection(self):
        from consultasdeveiculos_sdk.parser.postman_parser import PostmanParser

        parser = PostmanParser()
        collection = {
            "info": {"name": "Test"},
            "item": [
                {
                    "name": "Test Request",
                    "request": {
                        "method": "POST",
                        "url": {"raw": "https://api.example.com/test"},
                        "body": {
                            "mode": "urlencoded",
                            "urlencoded": [
                                {"key": "param1", "value": "value1"}
                            ],
                        },
                    },
                }
            ],
        }
        endpoints = parser.parse(collection)
        assert len(endpoints) == 1
        assert endpoints[0]["method"] == "POST"
