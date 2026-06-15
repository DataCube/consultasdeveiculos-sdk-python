"""
Exemplo básico de uso da SDK

Demonstra:
- Inicialização com auth_token
- Chamadas via __getattr__ usando slugs
- Modo sandbox para testes
- Tratamento de erros
"""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from consultasdeveiculos_sdk import ConsultadeveiculosSDK, SDKError


def main():
    try:
        # Modo sandbox para teste (ignora auth_token)
        client = ConsultadeveiculosSDK(
            auth_token=os.environ.get("API_TOKEN", "test"),
            sandbox=True,
        )

        # Consulta de Veículo - Agregados
        veiculo = client.veiculos_agregados(placa="LPH9883")

        import json
        print("Response:")
        print(json.dumps(veiculo.get("data"), indent=2, ensure_ascii=False))

    except SDKError as error:
        print(f"❌ Erro: {error}")
        print(f"   Código: {error.error_code}")
        if error.details:
            print(f"   Detalhes: {error.details}")
    except Exception as error:
        print(f"❌ Erro: {error}")


if __name__ == "__main__":
    main()
