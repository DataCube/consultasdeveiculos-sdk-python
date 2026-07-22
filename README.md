# consultasdeveiculos-sdk

SDK Python para a API [Consultas de Veículos](https://www.consultasdeveiculos.com) (Datacube).

Acesso simplificado a **176+ endpoints** de consulta veicular, CNH, cadastros, crédito e mais.

## Instalação

```bash
pip install consultasdeveiculos-sdk
```

## Uso Rápido

```python
from consultasdeveiculos_sdk import ConsultadeveiculosSDK

client = ConsultadeveiculosSDK(auth_token="SEU_TOKEN")

# Consulta veicular por placa
result = client.veiculos_agregados(placa="ABC1234")
print(result)

# Consulta CNH
cnh = client.cnh_dados(cpf="12345678900")
print(cnh)
```

## Modo Sandbox

Para testes sem consumir créditos:

```python
client = ConsultadeveiculosSDK(sandbox=True)
result = client.veiculos_agregados(placa="ABC1234")
# Retorna dados simulados
```

## CLI

```bash
# Lista endpoints disponíveis
consultasdeveiculos-sdk endpoints

# Filtra por namespace
consultasdeveiculos-sdk endpoints veiculos

# Saída JSON
consultasdeveiculos-sdk endpoints --json

# Verifica instalação
consultasdeveiculos-sdk doctor

# Versão
consultasdeveiculos-sdk version

# Atualiza especificação
consultasdeveiculos-sdk update

# Limpa cache
consultasdeveiculos-sdk clear-cache
```

## Explorar Endpoints

```python
client = ConsultadeveiculosSDK(sandbox=True)

# Informações gerais
info = client.get_info()
print(f"Endpoints: {info['slugsCount']}")

# Listar todos os endpoints
endpoints = client.list_endpoints()
for ep in endpoints[:5]:
    print(f"  {ep['slug']} - {ep['name']}")

# Listar todos os slugs
slugs = client.list_slugs()
```

## Tratamento de Erros

```python
from consultasdeveiculos_sdk import (
    ConsultadeveiculosSDK,
    AuthenticationError,
    RateLimitError,
    EndpointNotFoundError,
)

try:
    result = client.veiculos_agregados(placa="ABC1234")
except AuthenticationError:
    print("Token inválido ou expirado")
except RateLimitError as e:
    print(f"Rate limit - tente novamente em {e.details.get('retry_after')}s")
except EndpointNotFoundError:
    print("Endpoint não existe")
```

## Requisitos

- Python 3.10+
- requests >= 2.28.0

## Links

- [Documentação da API](https://www.consultasdeveiculos.com/documentation)
- [Painel](https://painel.consultasdeveiculos.com)
- [PyPI](https://pypi.org/project/consultasdeveiculos-sdk/)

## Licença

MIT
