"""
consultasdeveiculos-sdk - SDK Python Dinâmica Baseada em Postman

Runtime Engine que consome endpoints definidos em coleções Postman
sem necessidade de implementação manual de cada endpoint.

TODAS as funções são geradas dinamicamente via __getattr__.
Nenhuma função é declarada diretamente na classe.

Exemplo:
    # Modo produção
    from consultasdeveiculos_sdk import ConsultadeveiculosSDK

    client = ConsultadeveiculosSDK(auth_token="TOKEN")
    result = client.veiculos_agregados(placa="ABC1234")

    # Modo sandbox (ignora auth_token)
    client = ConsultadeveiculosSDK(sandbox=True)
"""

from consultasdeveiculos_sdk.core.sdk import ConsultadeveiculosSDK, SDK
from consultasdeveiculos_sdk.errors import (
    SDKError,
    AuthenticationError,
    ValidationError,
    RateLimitError,
    EndpointNotFoundError,
    SpecificationError,
)

__version__ = "1.0.0"
__all__ = [
    "ConsultadeveiculosSDK",
    "SDK",
    "SDKError",
    "AuthenticationError",
    "ValidationError",
    "RateLimitError",
    "EndpointNotFoundError",
    "SpecificationError",
]
