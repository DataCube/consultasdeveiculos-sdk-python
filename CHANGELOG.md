# Changelog

Todas as mudanças notáveis do projeto serão documentadas neste arquivo.

## [1.0.0] - 2025-01-01

### Adicionado
- SDK Python completa para API Consultas de Veículos
- Suporte a todos os 176+ endpoints da API Datacube
- CLI com comandos: endpoints, doctor, version, update, clear-cache
- Modo sandbox para testes sem consumir créditos
- Parsing automático de Postman Collection
- Cache local de endpoints
- Tratamento de erros tipado (AuthenticationError, RateLimitError, etc.)
- Retry automático em erros 429 (rate limit)
- Exemplos de uso
