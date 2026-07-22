"""
Exemplo de exploração de endpoints
"""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from consultasdeveiculos_sdk import ConsultadeveiculosSDK


def main():
    client = ConsultadeveiculosSDK(sandbox=True)

    # Informações da SDK
    info = client.get_info()
    print(f"Versão: {info['runtimeVersion']}")
    print(f"Spec: {info['specVersion']}")
    print(f"Endpoints: {info['slugsCount']}")
    print()

    # Listar endpoints disponíveis
    endpoints = client.list_endpoints()
    print(f"Total de endpoints: {len(endpoints)}")
    for ep in endpoints[:5]:
        print(f"  • {ep['slug']} - {ep['name']}")
    print()

    # Listar todos os slugs
    slugs = client.list_slugs()
    print(f"Total de slugs: {len(slugs)}")
    print(f"Primeiros 10: {slugs[:10]}")


if __name__ == "__main__":
    main()
