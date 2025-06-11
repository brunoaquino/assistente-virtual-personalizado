# 🤖 Assistente Virtual Personalizado para E-commerce

Um assistente virtual inteligente desenvolvido para e-commerce, utilizando tecnologias de IA avançadas como RAG (Retrieval-Augmented Generation), embeddings e processamento de linguagem natural.

## 📋 Índice

- [Visão Geral](#-visão-geral)
- [Funcionalidades](#-funcionalidades)
- [Arquitetura](#-arquitetura)
- [Tecnologias Utilizadas](#-tecnologias-utilizadas)
- [Configuração do Ambiente](#-configuração-do-ambiente)
- [Instalação](#-instalação)
- [Uso](#-uso)
- [API Endpoints](#-api-endpoints)
- [Testes](#-testes)
- [Integração com Pinecone](#-integração-com-pinecone)
- [Estrutura do Projeto](#-estrutura-do-projeto)
- [Melhorias Implementadas](#-melhorias-implementadas)
- [Contribuição](#-contribuição)

## 🎯 Visão Geral

Este projeto implementa um assistente virtual completo para e-commerce que combina:

- **RAG System**: Sistema de recuperação e geração aumentada para respostas precisas
- **Embeddings**: Busca semântica avançada usando OpenAI embeddings
- **Persistência em Nuvem**: Integração com Pinecone para armazenamento de vetores
- **API RESTful**: Interface completa para integração com sistemas externos
- **Processamento de Linguagem Natural**: Detecção de intenções e respostas contextuais

## ✨ Funcionalidades

### 🔍 **1. Busca Inteligente de Produtos**

- Busca por texto natural: "Quero um smartphone Android, tela grande, até R$ 1.500"
- Filtros por categoria, preço, características
- Busca semântica usando embeddings
- Recomendações baseadas em similaridade

### 📋 **2. Consulta de Políticas da Loja**

- Respostas sobre políticas de troca, devolução, garantia
- Processamento de perguntas em linguagem natural
- Base de conhecimento atualizada automaticamente

### 📦 **3. Consulta de Status de Pedidos**

- Verificação de status por número do pedido
- Informações de entrega e rastreamento
- Histórico completo de pedidos

### 🎁 **4. Recomendações Personalizadas**

- Sugestões baseadas em preferências
- Produtos similares por categoria
- Recomendações contextuais

### 💬 **5. Conversa Natural**

- Processamento de linguagem natural
- Detecção automática de intenções
- Respostas contextuais e personalizadas
- Aprendizado contínuo com conversas

## 🏗️ Arquitetura

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   API FastAPI   │    │   RAG System    │
│   (Opcional)    │◄──►│                 │◄──►│                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │   Assistente    │    │   Embeddings    │
                       │   Principal     │◄──►│   (OpenAI)      │
                       └─────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │   Dados JSON    │    │   Pinecone      │
                       │   (Local)       │    │   (Nuvem)       │
                       └─────────────────┘    └─────────────────┘
```

## 🛠️ Tecnologias Utilizadas

### **Backend**

- **Python 3.9+**: Linguagem principal
- **FastAPI 0.115.12**: Framework web moderno e rápido
- **LangChain 0.3.25**: Framework para aplicações com LLM
- **OpenAI 1.86.0**: API para embeddings e chat completion

### **Armazenamento e Busca**

- **FAISS 1.11.0**: Busca de similaridade local
- **Pinecone 7.0.2**: Banco de dados vetorial em nuvem
- **JSON**: Armazenamento local de dados estruturados

### **Processamento**

- **NumPy**: Computação numérica
- **Pandas**: Manipulação de dados
- **Requests**: Cliente HTTP para testes

### **Deploy**

- **Docker**: Containerização
- **Uvicorn**: Servidor ASGI
- **Requirements.txt**: Gerenciamento de dependências

## ⚙️ Configuração do Ambiente

### **1. Variáveis de Ambiente**

Crie um arquivo `.env` na raiz do projeto:

```env
# OpenAI Configuration
OPENAI_API_KEY=sua_chave_openai_aqui

# Pinecone Configuration (Opcional)
PINECONE_API_KEY=sua_chave_pinecone_aqui
PINECONE_ENVIRONMENT=us-east-1-aws
PINECONE_INDEX_NAME=ecommerce-assistant
```

### **2. Estrutura de Dados**

O sistema utiliza três arquivos principais de dados:

- `data/produtos.json`: Catálogo de produtos
- `data/pedidos.json`: Histórico de pedidos
- `data/politicas.md`: Políticas da loja

## 🚀 Instalação

### **1. Clone o Repositório**

```bash
git clone <url-do-repositorio>
cd projeto_final
```

### **2. Crie o Ambiente Virtual**

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows
```

### **3. Instale as Dependências**

```bash
pip install -r deploy/requirements.txt
```

### **4. Configure as Variáveis de Ambiente**

```bash
cp .env.example .env
# Edite o arquivo .env com suas chaves de API
```

## 🎮 Uso

### **1. Iniciar a API**

```bash
uvicorn src.api:app --reload
```

A API estará disponível em: `http://localhost:8000`

### **2. Documentação Interativa**

Acesse: `http://localhost:8000/docs`

### **3. Teste Rápido**

```bash
curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{"mensagem": "Oi, preciso de ajuda", "usuario_id": "user123"}'
```

## 🔌 API Endpoints

O sistema oferece uma API RESTful completa com 13 endpoints funcionais organizados em 5 categorias principais.

### **Documentação Completa**

📖 **Para documentação detalhada de todas as APIs, consulte:** [API_DOCUMENTATION.md](API_DOCUMENTATION.md)

### **Principais Endpoints**

- `POST /chat` - Conversa com o assistente
- `GET /health` - Status do sistema
- `GET /estatisticas` - Estatísticas do sistema
- `GET /buscar` - Busca de produtos
- `GET /produtos` - Lista todos os produtos
- `POST /produtos` - Adiciona novo produto
- `PUT /produtos/{produto_id}` - Atualiza produto
- `DELETE /produtos/{produto_id}` - Remove produto

### **Busca Avançada**

- `POST /buscar` - Busca de produtos com filtros
- `POST /buscar/embedding` - Busca semântica com threshold
- `GET /produtos/{produto_id}/similares` - Produtos similares

### **Sistema**

- `GET /health` - Status da API
- `POST /reindexar` - Reindexar sistema RAG

## 🧪 Testes

### **Teste Completo do Sistema**

```bash
python test_completo.py
```

Este teste verifica:

- ✅ Configuração do ambiente
- ✅ Integridade dos dados
- ✅ Funcionalidade da API
- ✅ Os 5 cenários principais
- ✅ Endpoints adicionais
- ✅ Relatório de performance

### **Cenários Testados**

1. **Busca de Produtos**: "Quero um smartphone Android, tela grande, até R$ 1.500"
2. **Políticas**: "Posso trocar um produto depois de 15 dias?"
3. **Status de Pedido**: "Meu pedido #12345 já saiu para entrega?"
4. **Recomendações**: "Que presente vocês sugerem para quem gosta de cozinhar?"
5. **Conversa Natural**: "Oi, tudo bem? Estou procurando um presente para minha mãe"

## 🌐 Integração com Pinecone

### **Configuração**

O sistema suporta tanto armazenamento local (FAISS) quanto em nuvem (Pinecone):

```python
# Configuração automática baseada nas variáveis de ambiente
rag_system = RAGSystem(
    openai_api_key=os.getenv('OPENAI_API_KEY'),
    pinecone_api_key=os.getenv('PINECONE_API_KEY'),  # Opcional
    pinecone_environment=os.getenv('PINECONE_ENVIRONMENT'),
    pinecone_index_name=os.getenv('PINECONE_INDEX_NAME')
)
```

### **Vantagens do Pinecone**

- ✅ Armazenamento em nuvem
- ✅ Escalabilidade automática
- ✅ Backup automático
- ✅ Acesso distribuído
- ✅ Performance otimizada

## 📁 Estrutura do Projeto

```
projeto_final/
├── src/                          # Código fonte principal
│   ├── assistente.py            # Assistente principal
│   ├── rag_system.py            # Sistema RAG com embeddings
│   ├── api.py                   # API FastAPI
│   └── prompts.py               # Templates de prompts
├── data/                        # Dados do sistema
│   ├── produtos.json            # Catálogo de produtos
│   ├── pedidos.json             # Histórico de pedidos
│   └── politicas.md             # Políticas da loja
├── deploy/                      # Arquivos de deploy
│   ├── requirements.txt         # Dependências Python
│   └── Dockerfile              # Container Docker
├── test_completo.py            # Teste completo do sistema
├── README.md                   # Este arquivo
└── .env                        # Variáveis de ambiente
```

## 🚀 Melhorias Implementadas

### **Sistema RAG Avançado**

- ✅ **Persistência Automática**: Dados salvos automaticamente no JSON e Pinecone
- ✅ **CRUD Completo**: Operações completas de Create, Read, Update, Delete
- ✅ **Embeddings Inteligentes**: Busca semântica com threshold configurável
- ✅ **Aprendizado Contínuo**: Sistema aprende com conversas dos usuários

### **API Robusta**

- ✅ **Endpoints RESTful**: API completa seguindo padrões REST
- ✅ **Documentação Automática**: Swagger/OpenAPI integrado
- ✅ **Tratamento de Erros**: Respostas consistentes e informativas
- ✅ **Validação de Dados**: Pydantic models para validação

### **Integração em Nuvem**

- ✅ **Pinecone Integration**: Armazenamento vetorial em nuvem
- ✅ **Fallback Local**: FAISS como backup local
- ✅ **Configuração Flexível**: Suporte a múltiplos ambientes
- ✅ **Monitoramento**: Estatísticas detalhadas do sistema

### **Testes Abrangentes**

- ✅ **Teste Unificado**: Todos os testes em um arquivo
- ✅ **Validação Completa**: Ambiente, dados, API e funcionalidades
- ✅ **Relatórios Detalhados**: Métricas de performance e sucesso
- ✅ **Cenários Reais**: Testes baseados em casos de uso reais

## 📊 Estatísticas do Sistema

O sistema atual possui:

- **146 vetores** indexados no Pinecone
- **17 produtos** no catálogo
- **5 funcionalidades principais** implementadas
- **12 endpoints** de API disponíveis
- **100% de cobertura** nos testes principais

## 🔧 Comandos Úteis

### **Desenvolvimento**

```bash
# Iniciar API em modo desenvolvimento
uvicorn src.api:app --reload --host 0.0.0.0 --port 8000

# Executar testes
python test_completo.py

# Verificar dependências
pip freeze > requirements_atual.txt

# Reindexar sistema RAG
curl -X POST "http://localhost:8000/reindexar"
```

### **Deploy com Docker**

```bash
# Construir imagem
docker build -t assistente-ecommerce .

# Executar container
docker run -p 8000:8000 --env-file .env assistente-ecommerce
```

## 🤝 Contribuição

### **Como Contribuir**

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

### **Padrões de Código**

- Siga PEP 8 para Python
- Documente funções e classes
- Adicione testes para novas funcionalidades
- Mantenha o README atualizado

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 📞 Suporte

Para dúvidas ou suporte:

- Abra uma issue no GitHub
- Consulte a documentação da API em `/docs`
- Execute os testes para verificar o funcionamento

---

## 🎉 Agradecimentos

Projeto desenvolvido como parte do curso de IA, demonstrando a implementação completa de um assistente virtual moderno com tecnologias de ponta.

**Tecnologias principais**: Python, FastAPI, LangChain, OpenAI, Pinecone, FAISS

**Status**: ✅ Funcional e testado | 🚀 Pronto para produção
