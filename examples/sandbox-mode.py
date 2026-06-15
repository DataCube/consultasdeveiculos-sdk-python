"""
Exemplo de modo sandbox
"""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from consultasdeveiculos_sdk import ConsultadeveiculosSDK


def main():
    # Modo sandbox - não faz chamadas reais
    client = ConsultadeveiculosSDK(sandbox=True)

    # Consultas retornam dados simulados
    result = client.veiculos_agregados(placa="ABC1234")
    print(f"Sandbox: {result.get('sandbox')}")
    print(f"Endpoint: {result.get('endpoint')}")
    print(f"Status: {result.get('status')}")


if __name__ == "__main__":
    main()
