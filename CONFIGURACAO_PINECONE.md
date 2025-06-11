# Configuração do Pinecone para Assistente Virtual

## 📌 Sobre

O sistema agora suporta **Pinecone** como vector store na nuvem, além do FAISS local. Com Pinecone, seus dados são persistidos automaticamente na nuvem, permitindo:

- ✅ **Persistência automática** - Dados salvos permanentemente na nuvem
- ✅ **Escalabilidade** - Suporta milhões de vetores
- ✅ **Performance** - Busca ultrarrápida por similaridade
- ✅ **Colaboração** - Compartilhamento entre diferentes instâncias

## 🚀 Como Configurar

### 1. Obter API Key do Pinecone

1. Acesse [pinecone.io](https://pinecone.io) e crie uma conta
2. No dashboard, crie um novo projeto
3. Copie sua **API Key**
4. Anote o **Environment** (ex: `gcp-starter`)

### 2. Configurar Variáveis de Ambiente

```bash
# Obrigatório
export OPENAI_API_KEY="sua_openai_api_key_aqui"

# Para usar Pinecone (opcional)
export PINECONE_API_KEY="sua_pinecone_api_key_aqui"
export PINECONE_ENV="gcp-starter"  # ou seu environment
export PINECONE_INDEX="assistente-ecommerce"  # nome do índice
```

### 3. Instalar Dependências

```bash
# O pinecone-client já está no requirements.txt
pip install -r deploy/requirements.txt
```

## 📊 Comportamento do Sistema

### Com Pinecone Configurado:

- ✅ Dados persistidos automaticamente na nuvem
- ✅ Índice criado automaticamente se não existir
- ✅ Sincronização em tempo real
- ✅ Backup automático

### Sem Pinecone (FAISS local):

- ⚠️ Dados salvos apenas localmente
- ⚠️ Perda de dados ao reiniciar sem backup
- ✅ Funciona offline
- ✅ Mais rápido para desenvolvimento

## 🔧 Testando a Configuração

### 1. Verificar Status

```bash
curl http://localhost:8000/estatisticas
```

Resposta com Pinecone:

```json
{
  "rag": {
    "usando_pinecone": true,
    "pinecone_disponivel": true,
    "tipo_vector_store": "Pinecone (nuvem)",
    "pinecone_index_name": "assistente-ecommerce",
    "total_vetores_pinecone": 45
  }
}
```

### 2. Adicionar Produto via API

```bash
curl -X POST "http://localhost:8000/admin/produto" \
  -H "Content-Type: application/json" \
  -d '{
    "id": "test-123",
    "nome": "Produto Teste Pinecone",
    "categoria": "teste",
    "preco": 99.99,
    "descricao": "Produto para testar persistência no Pinecone",
    "especificacoes": {"cor": "azul"},
    "disponivel": true
  }'
```

### 3. Buscar Produto

```bash
curl "http://localhost:8000/buscar?q=teste pinecone"
```

Se configurado corretamente, o produto será encontrado mesmo após reiniciar a aplicação!

## 🔍 Logs de Verificação

Ao iniciar com Pinecone, você verá:

```
INFO - Pinecone inicializado: índice 'assistente-ecommerce'
INFO - Indexados 45 produtos no Pinecone
INFO - Sistema RAG inicializado com Pinecone
```

Sem Pinecone:

```
INFO - Indexados 45 produtos no FAISS local
INFO - Sistema RAG inicializado com FAISS local
```

## ⚡ Vantagens do Pinecone

1. **Persistência Real**: Dados nunca se perdem
2. **Escalabilidade**: Suporta milhões de produtos
3. **Performance**: Sub-second query response
4. **Multi-instância**: Várias APIs usando mesmo índice
5. **Backup Automático**: Dados replicados automaticamente

## 🛠️ Troubleshooting

### Erro: "Pinecone não está disponível"

```bash
pip install pinecone-client
```

### Erro: "PINECONE_API_KEY não configurada"

```bash
export PINECONE_API_KEY="sua_api_key_aqui"
```

### Erro: "Failed to connect to Pinecone"

- Verifique se a API key está correta
- Confirme o environment (gcp-starter, us-east-1, etc.)
- Teste conectividade de rede

### Performance Lenta

- Usar environment geograficamente próximo
- Verificar quota do plano Pinecone
- Considerar batch updates para grandes volumes

## 📈 Monitoramento

Use o dashboard do Pinecone para monitorar:

- Número de vetores armazenados
- Queries por segundo
- Latência média
- Uso de storage

---

**🎯 Resultado**: Sistema totalmente funcional com persistência na nuvem via Pinecone!
