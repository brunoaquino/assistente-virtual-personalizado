# 🔌 Documentação Completa das APIs

## 📋 Visão Geral

O Assistente Virtual E-commerce possui **18 endpoints** organizados em 5 categorias principais:

- **📋 Informações Básicas** (3 endpoints)
- **💬 Chat e Conversação** (2 endpoints)
- **📊 Estatísticas** (1 endpoint)
- **🔍 Busca de Produtos** (3 endpoints)
- **🛠️ Administração** (4 endpoints)

---

## 📋 Informações Básicas

### `GET /`

**Descrição**: Endpoint raiz com informações da API

**Exemplo:**

```bash
curl -X GET "http://localhost:8000/"
```

**Resposta:**

```json
{
  "nome": "Assistente Virtual E-commerce",
  "versao": "1.0.0",
  "status": "ativo",
  "timestamp": "2025-01-11T18:58:44.123456",
  "endpoints": {
    "chat": "/chat",
    "historico": "/sessao/{id_sessao}/historico",
    "estatisticas": "/estatisticas",
    "saude": "/health"
  }
}
```

### `GET /health`

**Descrição**: Health check da aplicação

**Exemplo:**

```bash
curl -X GET "http://localhost:8000/health"
```

**Resposta (Sucesso):**

```json
{
  "status": "saudavel",
  "timestamp": "2025-01-11T18:58:44.123456",
  "componentes": {
    "assistente": "ativo",
    "rag_sistema": "ativo",
    "llm": "ativo"
  }
}
```

**Resposta (Erro):**

```json
{
  "status": "erro",
  "erro": "Descrição do erro",
  "timestamp": "2025-01-11T18:58:44.123456"
}
```

### `GET /docs`

**Descrição**: Documentação interativa Swagger/OpenAPI

**Exemplo:**

```bash
# Acesse no browser: http://localhost:8000/docs
```

---

## 💬 Chat e Conversação

### `POST /chat`

**Descrição**: Endpoint principal para conversar com o assistente

**Parâmetros:**

- `mensagem` (string, obrigatório): Mensagem do usuário
- `id_sessao` (string, opcional): ID da sessão
- `contexto` (object, opcional): Contexto adicional

**Exemplo Básico:**

```bash
curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{
       "mensagem": "Oi, preciso de ajuda",
       "id_sessao": "user123"
     }'
```

**Exemplos dos 5 Cenários Principais:**

#### 1. Busca de Produtos

```bash
curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{
       "mensagem": "Quero um smartphone Android, tela grande, até R$ 1.500",
       "id_sessao": "user123"
     }'
```

#### 2. Consulta de Políticas

```bash
curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{
       "mensagem": "Posso trocar um produto depois de 15 dias?",
       "id_sessao": "user456"
     }'
```

#### 3. Status de Pedido

```bash
curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{
       "mensagem": "Meu pedido #12345 já saiu para entrega?",
       "id_sessao": "user789"
     }'
```

#### 4. Recomendações

```bash
curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{
       "mensagem": "Que presente vocês sugerem para quem gosta de cozinhar?",
       "id_sessao": "user101"
     }'
```

#### 5. Conversa Natural

```bash
curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{
       "mensagem": "Oi, tudo bem? Estou procurando um presente para minha mãe",
       "id_sessao": "user202"
     }'
```

**Resposta:**

```json
{
  "resposta": "Olá! Como posso ajudá-lo hoje?",
  "intencao": "saudacao",
  "dados": {
    "produtos_encontrados": [],
    "contexto": "conversa_inicial"
  },
  "sucesso": true,
  "id_sessao": "user123",
  "timestamp": "2025-01-11T18:58:44.123456",
  "erro": null
}
```

### `GET /sessao/{id_sessao}/historico`

**Descrição**: Obtém histórico de uma sessão específica

**Parâmetros:**

- `id_sessao` (string, obrigatório): ID da sessão

**Exemplo:**

```bash
curl -X GET "http://localhost:8000/sessao/user123/historico"
```

**Resposta:**

```json
{
  "id_sessao": "user123",
  "total_interacoes": 5,
  "historico": [
    {
      "timestamp": "2025-01-11T18:58:44.123456",
      "mensagem": "Oi, preciso de ajuda",
      "resposta": "Olá! Como posso ajudá-lo hoje?",
      "intencao": "saudacao"
    }
  ]
}
```

---

## 📊 Estatísticas e Monitoramento

### `GET /estatisticas`

**Descrição**: Obtém estatísticas completas do sistema

**Exemplo:**

```bash
curl -X GET "http://localhost:8000/estatisticas"
```

**Resposta:**

```json
{
  "sistema": {
    "total_sessoes": 150,
    "total_interacoes": 1250,
    "uptime": "2 days, 5 hours"
  },
  "rag": {
    "total_produtos": 17,
    "total_vetores": 146,
    "pinecone_conectado": true,
    "faiss_ativo": true
  },
  "sessoes_ativas": 25,
  "total_interacoes": 1250
}
```

---

## 🔍 Busca de Produtos

### `GET /buscar`

**Descrição**: Busca de produtos com filtros

**Parâmetros:**

- `q` (string, obrigatório): Termo de busca
- `categoria` (string, opcional): Filtro por categoria
- `preco_min` (float, opcional): Preço mínimo
- `preco_max` (float, opcional): Preço máximo
- `top_k` (int, opcional): Número de resultados (padrão: 5)

**Exemplos:**

```bash
# Busca simples
curl -X GET "http://localhost:8000/buscar?q=smartphone"

# Busca com filtros
curl -X GET "http://localhost:8000/buscar?q=notebook&categoria=Eletrônicos&preco_max=3000&top_k=5"
```

**Resposta:**

```json
{
  "produtos": [
    {
      "id": "PROD001",
      "nome": "Smartphone Samsung Galaxy",
      "categoria": "Eletrônicos",
      "preco": 1299.99,
      "descricao": "Smartphone com tela grande...",
      "score": 0.95
    }
  ],
  "total_encontrados": 1,
  "tempo_busca": 0.123,
  "filtros_aplicados": {
    "categoria": "Eletrônicos",
    "preco_max": 3000
  }
}
```

### `GET /buscar/embedding`

**Descrição**: Busca semântica usando embeddings

**Parâmetros:**

- `q` (string, obrigatório): Termo de busca
- `threshold` (float, opcional): Limite de similaridade (padrão: 0.6)
- `top_k` (int, opcional): Número de resultados (padrão: 5)

**Exemplo:**

```bash
curl -X GET "http://localhost:8000/buscar/embedding?q=celular%20barato&threshold=0.6&top_k=5"
```

**Resposta:**

```json
{
  "produtos": [
    {
      "id": "PROD001",
      "nome": "Smartphone Samsung Galaxy",
      "categoria": "Eletrônicos",
      "preco": 1299.99,
      "similarity_score": 0.87
    }
  ],
  "total_encontrados": 1,
  "threshold_usado": 0.6,
  "tempo_busca": 0.156
}
```

### `GET /produtos/{produto_id}/similares`

**Descrição**: Obtém produtos similares a um produto específico

**Parâmetros:**

- `produto_id` (string, obrigatório): ID do produto
- `top_k` (int, opcional): Número de resultados (padrão: 3)

**Exemplo:**

```bash
curl -X GET "http://localhost:8000/produtos/PROD001/similares?top_k=3"
```

**Resposta:**

```json
{
  "produto_referencia": {
    "id": "PROD001",
    "nome": "Smartphone Samsung Galaxy"
  },
  "produtos_similares": [
    {
      "id": "PROD002",
      "nome": "iPhone 13",
      "categoria": "Eletrônicos",
      "preco": 2999.99,
      "similarity_score": 0.92
    }
  ],
  "total_similares": 1
}
```

---

## 🛠️ Administração (CRUD de Produtos)

### `POST /admin/produto`

**Descrição**: Adiciona novo produto ao sistema

**Parâmetros:**

- `id` (string, obrigatório): ID único do produto
- `nome` (string, obrigatório): Nome do produto
- `categoria` (string, obrigatório): Categoria do produto
- `preco` (float, obrigatório): Preço do produto
- `descricao` (string, obrigatório): Descrição do produto
- `especificacoes` (object, obrigatório): Especificações técnicas
- `disponivel` (boolean, opcional): Se está disponível (padrão: true)

**Exemplo:**

```bash
curl -X POST "http://localhost:8000/admin/produto" \
     -H "Content-Type: application/json" \
     -d '{
       "id": "PROD999",
       "nome": "Produto Teste",
       "categoria": "Teste",
       "preco": 99.99,
       "descricao": "Produto para teste da API",
       "especificacoes": {
         "cor": "azul",
         "tamanho": "médio"
       },
       "disponivel": true
     }'
```

**Resposta:**

```json
{
  "sucesso": true,
  "mensagem": "Produto Produto Teste adicionado com sucesso",
  "produto_id": "PROD999"
}
```

### `PUT /admin/produto/{produto_id}`

**Descrição**: Atualiza produto existente

**Parâmetros:** (mesmos do POST)

**Exemplo:**

```bash
curl -X PUT "http://localhost:8000/admin/produto/PROD999" \
     -H "Content-Type: application/json" \
     -d '{
       "id": "PROD999",
       "nome": "Produto Teste Atualizado",
       "categoria": "Teste",
       "preco": 149.99,
       "descricao": "Produto atualizado via API",
       "especificacoes": {
         "cor": "vermelho",
         "tamanho": "grande"
       },
       "disponivel": true
     }'
```

**Resposta:**

```json
{
  "sucesso": true,
  "mensagem": "Produto PROD999 atualizado com sucesso"
}
```

### `DELETE /admin/produto/{produto_id}`

**Descrição**: Remove produto do sistema

**Parâmetros:**

- `produto_id` (string, obrigatório): ID do produto a ser removido

**Exemplo:**

```bash
curl -X DELETE "http://localhost:8000/admin/produto/PROD999"
```

**Resposta:**

```json
{
  "sucesso": true,
  "mensagem": "Produto PROD999 removido com sucesso"
}
```

### `POST /admin/reindexar`

**Descrição**: Reindexar todo o sistema RAG

**Exemplo:**

```bash
curl -X POST "http://localhost:8000/admin/reindexar"
```

**Resposta:**

```json
{
  "sucesso": true,
  "mensagem": "Reindexação iniciada em background"
}
```

---

## 🧪 Scripts de Teste

### Script Completo de Teste

Crie um arquivo `test_api.sh`:

```bash
#!/bin/bash

echo "🧪 Testando API do Assistente Virtual..."

# Health Check
echo "1. Health Check:"
curl -s "http://localhost:8000/health" | jq

# Chat
echo -e "\n2. Chat:"
curl -s -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{"mensagem": "Oi, preciso de ajuda", "id_sessao": "test"}' | jq

# Busca
echo -e "\n3. Busca:"
curl -s "http://localhost:8000/buscar?q=smartphone" | jq

# Estatísticas
echo -e "\n4. Estatísticas:"
curl -s "http://localhost:8000/estatisticas" | jq

echo -e "\n✅ Testes concluídos!"
```

Execute com: `chmod +x test_api.sh && ./test_api.sh`

### Teste dos 5 Cenários Principais

```bash
#!/bin/bash

echo "🎯 Testando os 5 cenários principais..."

# Cenário 1: Busca de Produtos
echo "1. Busca de Produtos:"
curl -s -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{"mensagem": "Quero um smartphone Android, tela grande, até R$ 1.500", "id_sessao": "test1"}' | jq .resposta

# Cenário 2: Políticas
echo -e "\n2. Políticas:"
curl -s -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{"mensagem": "Posso trocar um produto depois de 15 dias?", "id_sessao": "test2"}' | jq .resposta

# Cenário 3: Status de Pedido
echo -e "\n3. Status de Pedido:"
curl -s -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{"mensagem": "Meu pedido #12345 já saiu para entrega?", "id_sessao": "test3"}' | jq .resposta

# Cenário 4: Recomendações
echo -e "\n4. Recomendações:"
curl -s -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{"mensagem": "Que presente vocês sugerem para quem gosta de cozinhar?", "id_sessao": "test4"}' | jq .resposta

# Cenário 5: Conversa Natural
echo -e "\n5. Conversa Natural:"
curl -s -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{"mensagem": "Oi, tudo bem? Estou procurando um presente para minha mãe", "id_sessao": "test5"}' | jq .resposta

echo -e "\n✅ Todos os cenários testados!"
```

---

## 📊 Resumo dos Endpoints

| Categoria  | Endpoint                   | Método | Descrição               |
| ---------- | -------------------------- | ------ | ----------------------- |
| **Básico** | `/`                        | GET    | Informações da API      |
| **Básico** | `/health`                  | GET    | Health check            |
| **Básico** | `/docs`                    | GET    | Documentação            |
| **Chat**   | `/chat`                    | POST   | Conversa principal      |
| **Chat**   | `/sessao/{id}/historico`   | GET    | Histórico de sessão     |
| **Stats**  | `/estatisticas`            | GET    | Estatísticas do sistema |
| **Busca**  | `/buscar`                  | GET    | Busca com filtros       |
| **Busca**  | `/buscar/embedding`        | GET    | Busca semântica         |
| **Busca**  | `/produtos/{id}/similares` | GET    | Produtos similares      |
| **Admin**  | `/admin/produto`           | POST   | Adicionar produto       |
| **Admin**  | `/admin/produto/{id}`      | PUT    | Atualizar produto       |
| **Admin**  | `/admin/produto/{id}`      | DELETE | Remover produto         |
| **Admin**  | `/admin/reindexar`         | POST   | Reindexar sistema       |

**Total: 13 endpoints funcionais** 🚀

---

## 🔗 Links Úteis

- **API Base**: `http://localhost:8000`
- **Documentação**: `http://localhost:8000/docs`
- **Health Check**: `http://localhost:8000/health`
- **Repositório**: [GitHub](https://github.com/brunoaquino/assistente-virtual-personalizado)

---

**Última atualização**: Janeiro 2025
