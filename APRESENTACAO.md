# 📋 Apresentação do Projeto: ConsultadeveiculosSDK Python

## 🎯 O que é este projeto?

A **ConsultadeveiculosSDK** é uma biblioteca (SDK) para Python 3.10+ que permite consultar informações de veículos, pessoas e CNH através de uma API. 

**A grande inovação**: ela é **100% dinâmica**. Diferente de SDKs tradicionais onde cada função precisa ser escrita manualmente, aqui **todos os 179 endpoints são gerados automaticamente** a partir de uma coleção Postman.

---

## 🧠 Por que isso é importante?

### Problema tradicional:
Imagine que você tem uma API com 179 endpoints. No modelo tradicional, você precisaria:
- Escrever 179 funções manualmente
- Manter 179 funções atualizadas quando a API mudar
- Testar cada uma individualmente

### Nossa solução:
```
Coleção Postman → SDK lê automaticamente → 179 métodos disponíveis
```

Quando a API adiciona novos endpoints, basta atualizar o arquivo Postman — a SDK já funciona com eles, **sem alterar código**.

---

## 🧩 Design Patterns — Por que usamos?

**Design Patterns** são soluções prontas para problemas comuns em programação. Usar patterns deixa o código mais organizado, fácil de manter e de entender.

### Patterns usados neste projeto:

| Pattern | Onde usamos | Por quê? |
|---------|-------------|----------|
| **Magic Method (__getattr__)** | sdk.py | Intercepta chamadas de método e redireciona para o endpoint correto. Permite criar 179 métodos sem escrever nenhum. |
| **Registry** | EndpointRegistry | Catálogo central de endpoints. Qualquer parte do código consulta o mesmo lugar. |
| **Strategy** | Transport | Troca fácil entre HttpTransport (produção) e SandboxTransport (testes) sem mudar código. |
| **Factory** | sdk.py | Cria o Transport correto baseado nas opções (`sandbox=True` ou `False`). |

### Benefícios práticos:

```
SEM PATTERNS                          COM PATTERNS
─────────────────────────────────────────────────────────────
❌ Código espalhado                   ✅ Código organizado
❌ Difícil de testar                  ✅ Fácil de testar (Strategy)
❌ Muita repetição                    ✅ Zero repetição (__getattr__)
❌ Mudança quebra tudo                ✅ Mudança isolada
❌ Novo dev demora entender           ✅ Estrutura familiar
```

**Em resumo:** Design Patterns são como "receitas de bolo" que todo desenvolvedor conhece. Quando usamos, qualquer pessoa consegue entender e manter o projeto mais facilmente.

---

## 🏗️ Arquitetura (Como funciona por dentro)

A SDK possui 4 camadas principais:

```
┌─────────────────────────────────────────────────────┐
│  1️⃣  INTERFACE                                      │
│      • CLI (linha de comando via argparse)          │
│      • Aplicação do cliente (seu código Python)     │
├─────────────────────────────────────────────────────┤
│  2️⃣  CORE (Cérebro da SDK)                          │
│      • sdk.py → Orquestra tudo                      │
│      • postman_loader.py → Lê a coleção Postman     │
│      • endpoint_registry.py → Registra os endpoints │
│      • config_manager.py → Gerencia configurações   │
├─────────────────────────────────────────────────────┤
│  3️⃣  PARSER (Interpretador)                         │
│      • postman_parser.py → Entende o formato Postman│
│      • folder_parser.py → Processa pastas           │
│      • request_parser.py → Extrai info dos requests │
├─────────────────────────────────────────────────────┤
│  4️⃣  TRANSPORT (Comunicação)                        │
│      • http_transport.py → Chamadas reais (requests)│
│      • sandbox_transport.py → Respostas simuladas   │
└─────────────────────────────────────────────────────┘
```

---

## 🧠 Detalhamento do CORE (Cérebro da SDK)

O CORE é onde toda a "inteligência" da SDK acontece. Cada componente tem uma responsabilidade específica:

### 📌 sdk.py — O Maestro

**Localização:** `src/consultasdeveiculos_sdk/core/sdk.py`

É o ponto de entrada principal. Quando você faz `ConsultadeveiculosSDK()`, este arquivo:

1. **Valida as credenciais** — Verifica se o token foi fornecido (ou se está em modo sandbox)
2. **Coordena a inicialização** — Chama os outros componentes na ordem correta
3. **Implementa o __getattr__** — Intercepta chamadas como `client.veiculos_agregados()` e as direciona
4. **Expõe métodos auxiliares** — `help()`, `list_endpoints()`, `get_info()`

```python
# Fluxo interno do sdk.py
def __init__(self, auth_token=None, sandbox=False, **options):
    # 1. Armazena token em atributo privado
    # 2. Inicializa ConfigManager
    # 3. Carrega especificação Postman
    # 4. Registra endpoints no EndpointRegistry
    # 5. Cria o Transport apropriado (Http ou Sandbox)
```

---

### 📌 config_manager.py — O Guardião das Configurações

**Localização:** `src/consultasdeveiculos_sdk/core/config_manager.py`

Gerencia todas as configurações da SDK de forma centralizada:

| Responsabilidade | Descrição |
|------------------|-----------|
| **Armazenar opções** | timeout, base_url, max_retries, etc. |
| **Localizar arquivos** | Encontra o `postman.json` no diretório correto |
| **Gerenciar cache** | Define onde ficam arquivos em cache |
| **Extrair versões** | Lê a versão da especificação do nome do arquivo |

```python
# Exemplo de uso interno
cm = ConfigManager({
    "timeout": 30000,
    "max_retries": 3,
})

cm.get("timeout")              # 30000
cm.get_cache_dir()             # Retorna path do cache
cm.find_postman_file(path)     # Localiza postman.json
```

---

### 📌 postman_loader.py — O Leitor de Especificações

**Localização:** `src/consultasdeveiculos_sdk/core/postman_loader.py`

Responsável por carregar e interpretar a coleção Postman:

```
postman.json (arquivo) 
    ↓
PostmanLoader.load()
    ↓
Dict Python com todos os endpoints parseados
```

**O que ele faz:**
- Lê o arquivo `spec/postman.json`
- Valida a estrutura do arquivo
- Delega o parsing para o `PostmanParser`
- Retorna um dict estruturado com todos os endpoints

---

### 📌 endpoint_registry.py — O Catálogo de Endpoints

**Localização:** `src/consultasdeveiculos_sdk/core/endpoint_registry.py`

Funciona como um "dicionário" que mapeia slugs para endpoints:

```
┌─────────────────────────────────────────────────────────────┐
│                    EndpointRegistry                         │
├─────────────────────────────────────────────────────────────┤
│  "veiculos_agregados"      → { url, method, params, ... }  │
│  "veiculos_debitos_sp"     → { url, method, params, ... }  │
│  "cnh_nacional_simples"    → { url, method, params, ... }  │
│  "pessoas_nome"            → { url, method, params, ... }  │
│  ... (179 endpoints)                                        │
└─────────────────────────────────────────────────────────────┘
```

**Métodos principais:**
| Método | O que faz |
|--------|-----------|
| `register(endpoint)` | Adiciona um endpoint ao catálogo |
| `get(slug)` | Busca um endpoint pelo slug |
| `list_all()` | Lista todos os endpoints registrados |
| `list_by_namespace(ns)` | Lista endpoints por namespace |

---

### 🔄 Fluxo Completo do CORE

Quando você executa `client.veiculos_agregados(placa="ABC1234")`:

```
1. sdk.py (__getattr__) intercepta a chamada "veiculos_agregados"
         ↓
2. _slug_map["veiculos_agregados"] busca a definição
         ↓
3. Transport.build_body() monta a requisição HTTP
         ↓
4. Transport.request() envia a requisição (Http ou Sandbox)
         ↓
5. Resposta retornada ao usuário como dict
```

---

## ⚙️ A "Mágica" do __getattr__ Pattern

O coração da SDK usa o **Magic Method __getattr__** do Python. Funciona assim:

1. **Você escreve**: `client.veiculos_agregados(placa="ABC1234")`
2. **O __getattr__ intercepta** a chamada (pois o método não existe de verdade)
3. **Busca no _slug_map** qual endpoint corresponde ao slug
4. **Executa a requisição** via Transport
5. **Retorna o resultado** como dict

**Resultado**: você chama qualquer endpoint como se fosse um método nativo!

---

## 🛠️ Dois Modos de Operação

### 1️⃣ Modo Produção
```python
from consultasdeveiculos_sdk import ConsultadeveiculosSDK
import os

# Opção 1: Token direto (não recomendado em produção)
client = ConsultadeveiculosSDK(auth_token="SEU_TOKEN_AQUI")

# Opção 2: Token via variável de ambiente (RECOMENDADO)
# Defina: export API_TOKEN=seu_token_aqui
client = ConsultadeveiculosSDK(auth_token=os.environ["API_TOKEN"])

resultado = client.veiculos_agregados(placa="ABC1234")
# Faz chamada real à API
```

### 2️⃣ Modo Sandbox
```python
client = ConsultadeveiculosSDK(sandbox=True)
resultado = client.veiculos_agregados(placa="ABC1234")
# Retorna dados simulados, sem chamar a API real
```

O modo Sandbox é perfeito para:
- Desenvolvimento sem gastar créditos da API
- Testes automatizados
- Demonstrações para clientes

---

## 📁 Estrutura do Projeto

| Pasta/Arquivo | Função |
|---------------|--------|
| `src/consultasdeveiculos_sdk/core/` | Componentes principais (SDK, ConfigManager, etc.) |
| `src/consultasdeveiculos_sdk/parser/` | Interpretação da coleção Postman |
| `src/consultasdeveiculos_sdk/transport/` | Camada de comunicação HTTP (requests) |
| `src/consultasdeveiculos_sdk/errors/` | Tratamento de erros padronizado |
| `src/consultasdeveiculos_sdk/cli/` | Comandos de terminal (argparse) |
| `spec/` | Coleção Postman (fonte da verdade) |
| `examples/` | Exemplos de uso |
| `tests/` | Testes automatizados (pytest) |

---

## 🔐 Segurança

- **Tokens nunca são expostos** em logs, erros ou `json.dumps()`
- Atributo `_auth_token` é privado (invisível externamente)
- Dados sensíveis são sanitizados automaticamente nas mensagens de erro
- Validação obrigatória de token em modo produção

---

## 🎁 Funcionalidades Auxiliares

```python
client.help()                         # Exibe ajuda completa
client.help("veiculos")               # Filtra endpoints de veículos
client.list_endpoints()               # Lista todos os endpoints
client.get_info()                     # Informações da SDK
client.list_slugs()                   # Lista apenas os slugs
client.has_endpoint("veiculos_agregados")  # Verifica se existe
```

---

## 📊 Números do Projeto

| Métrica | Valor |
|---------|-------|
| Endpoints disponíveis | 179 |
| Dependências (produção) | 1 (requests) |
| Python mínimo | 3.10 |
| Funções hardcoded | 0 (tudo dinâmico!) |

---

## 🎯 Resumo Executivo

> **ConsultadeveiculosSDK Python** é uma SDK inteligente que elimina código repetitivo ao gerar métodos automaticamente a partir do Postman. Isso significa **menos manutenção**, **atualizações instantâneas** quando a API muda, e uma experiência de desenvolvimento moderna e fluida.

---

## 📖 Como Usar (Exemplo Rápido)

```python
from consultasdeveiculos_sdk import ConsultadeveiculosSDK

# Inicializa a SDK
client = ConsultadeveiculosSDK(auth_token="SEU_TOKEN_AQUI")

# Consulta veículo por placa
veiculo = client.veiculos_agregados(placa="ABC1234")
print(veiculo)

# Consulta CNH
cnh = client.cnh_nacional_simples(cnh="12345678901", data_nascimento="01/01/1990")
print(cnh)

# Consulta pessoa por CPF
pessoa = client.pessoas_nome(cpf="12345678900")
print(pessoa)
```

---

## 🔧 Comandos CLI Disponíveis

```bash
# Verifica status da instalação
consultasdeveiculos-sdk doctor

# Lista endpoints disponíveis
consultasdeveiculos-sdk endpoints

# Filtra por namespace
consultasdeveiculos-sdk endpoints veiculos

# Saída JSON
consultasdeveiculos-sdk endpoints --json

# Modo verbose
consultasdeveiculos-sdk endpoints -v

# Atualiza coleção Postman
consultasdeveiculos-sdk update

# Limpa cache
consultasdeveiculos-sdk clear-cache --force

# Mostra versão
consultasdeveiculos-sdk version
```

---

*Documento gerado para apresentação do projeto ConsultadeveiculosSDK Python*
*Versão: 1.0.0 | Data: Junho 2026*
