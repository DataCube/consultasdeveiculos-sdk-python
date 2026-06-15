"""
Exemplo de tratamento de erros
"""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from consultasdeveiculos_sdk import (
    ConsultadeveiculosSDK,
    SDKError,
    AuthenticationError,
    EndpointNotFoundError,
)


def main():
    # 1. Erro de autenticação
    print("1. Testando erro de autenticação...")
    try:
        client = ConsultadeveiculosSDK()  # Sem token
    except AuthenticationError as e:
        print(f"   ✅ Capturado: {e}")
        print(f"   Código: {e.error_code}")
    print()

    # 2. Endpoint não encontrado
    print("2. Testando endpoint não encontrado...")
    client = ConsultadeveiculosSDK(sandbox=True)
    try:
        client.execute_by_slug("endpoint_que_nao_existe")
    except EndpointNotFoundError as e:
        print(f"   ✅ Capturado: {e}")
        print(f"   Código: {e.error_code}")
    print()

    # 3. Erro genérico
    print("3. Testando SDKError...")
    try:
        raise SDKError("Erro de teste", "TEST_ERROR", {"info": "dados"})
    except SDKError as e:
        print(f"   ✅ Capturado: {e}")
        print(f"   Dict: {e.to_dict()}")


if __name__ == "__main__":
    main()
