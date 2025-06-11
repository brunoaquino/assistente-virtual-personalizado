"""
API FastAPI para o Assistente Virtual
Endpoints REST para interação com o assistente
"""

import os
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn

from .assistente import AssistenteVirtual

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Modelos Pydantic
class MensagemRequest(BaseModel):
    mensagem: str
    id_sessao: Optional[str] = None
    contexto: Optional[Dict[str, Any]] = None

class MensagemResponse(BaseModel):
    resposta: str
    intencao: str
    dados: Dict[str, Any]
    sucesso: bool
    id_sessao: str
    timestamp: str
    erro: Optional[str] = None

class ProdutoRequest(BaseModel):
    id: str
    nome: str
    categoria: str
    preco: float
    descricao: str
    especificacoes: Dict[str, Any]
    disponivel: bool = True

class EstatisticasResponse(BaseModel):
    sistema: Dict[str, Any]
    rag: Dict[str, Any]
    sessoes_ativas: int
    total_interacoes: int

# Inicialização da aplicação
app = FastAPI(
    title="Assistente Virtual E-commerce",
    description="API para assistente virtual inteligente de e-commerce",
    version="1.0.0"
)

# Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instância global do assistente
assistente: Optional[AssistenteVirtual] = None

def get_assistente() -> AssistenteVirtual:
    """Dependency para obter instância do assistente"""
    global assistente
    if assistente is None:
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            raise HTTPException(
                status_code=500, 
                detail="OPENAI_API_KEY não configurada"
            )
        
        pinecone_api_key = os.getenv("PINECONE_API_KEY")
        pinecone_env = os.getenv("PINECONE_ENV", "gcp-starter")
        pinecone_index = os.getenv("PINECONE_INDEX", "assistente-ecommerce")
        
        assistente = AssistenteVirtual(
            openai_api_key=openai_api_key,
            pinecone_api_key=pinecone_api_key,
            pinecone_env=pinecone_env,
            pinecone_index=pinecone_index
        )
    
    return assistente

@app.on_event("startup")
async def startup_event():
    """Inicialização da aplicação"""
    logger.info("Iniciando Assistente Virtual...")
    try:
        # Força inicialização do assistente
        get_assistente()
        logger.info("Assistente Virtual iniciado com sucesso!")
    except Exception as e:
        logger.error(f"Erro ao iniciar assistente: {e}")

@app.get("/")
async def root():
    """Endpoint raiz com informações da API"""
    return {
        "nome": "Assistente Virtual E-commerce",
        "versao": "1.0.0",
        "status": "ativo",
        "timestamp": datetime.now().isoformat(),
        "endpoints": {
            "chat": "/chat",
            "historico": "/sessao/{id_sessao}/historico",
            "estatisticas": "/estatisticas",
            "saude": "/health"
        }
    }

@app.get("/health")
async def health_check():
    """Health check da aplicação"""
    try:
        assistant = get_assistente()
        return {
            "status": "saudavel",
            "timestamp": datetime.now().isoformat(),
            "componentes": {
                "assistente": "ativo",
                "rag_sistema": "ativo" if assistant.rag_system else "inativo",
                "llm": "ativo"
            }
        }
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "erro",
                "erro": str(e),
                "timestamp": datetime.now().isoformat()
            }
        )

@app.post("/chat", response_model=MensagemResponse)
async def chat(
    request: MensagemRequest,
    background_tasks: BackgroundTasks,
    assistant: AssistenteVirtual = Depends(get_assistente)
):
    """
    Endpoint principal para chat com o assistente
    """
    try:
        # Gera ID da sessão se não fornecido
        id_sessao = request.id_sessao or str(uuid.uuid4())
        
        # Processa mensagem
        resultado = assistant.processar_mensagem(
            mensagem=request.mensagem,
            id_sessao=id_sessao
        )
        
        # Adiciona tarefa em background para logging
        background_tasks.add_task(
            log_interacao,
            id_sessao=id_sessao,
            mensagem=request.mensagem,
            resposta=resultado,
            contexto=request.contexto
        )
        
        return MensagemResponse(
            resposta=resultado["resposta"],
            intencao=resultado["intencao"],
            dados=resultado["dados"],
            sucesso=resultado["sucesso"],
            id_sessao=id_sessao,
            timestamp=datetime.now().isoformat(),
            erro=resultado.get("erro")
        )
        
    except Exception as e:
        logger.error(f"Erro no chat: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno no processamento: {str(e)}"
        )

@app.get("/sessao/{id_sessao}/historico")
async def obter_historico(
    id_sessao: str,
    assistant: AssistenteVirtual = Depends(get_assistente)
):
    """Obtém histórico de uma sessão específica"""
    try:
        historico = assistant.obter_historico_sessao(id_sessao)
        return {
            "id_sessao": id_sessao,
            "total_interacoes": len(historico),
            "historico": historico
        }
    except Exception as e:
        logger.error(f"Erro ao obter histórico: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao obter histórico: {str(e)}"
        )

@app.get("/estatisticas", response_model=EstatisticasResponse)
async def obter_estatisticas(
    assistant: AssistenteVirtual = Depends(get_assistente)
):
    """Obtém estatísticas do sistema"""
    try:
        stats_sistema = assistant.obter_estatisticas()
        stats_rag = assistant.rag_system.obter_estatisticas()
        
        return EstatisticasResponse(
            sistema=stats_sistema,
            rag=stats_rag,
            sessoes_ativas=stats_sistema["total_sessoes"],
            total_interacoes=stats_sistema["total_interacoes"]
        )
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao obter estatísticas: {str(e)}"
        )

@app.post("/admin/produto")
async def adicionar_produto(
    produto: ProdutoRequest,
    assistant: AssistenteVirtual = Depends(get_assistente)
):
    """Adiciona novo produto ao sistema (endpoint administrativo)"""
    try:
        produto_dict = produto.dict()
        assistant.rag_system.adicionar_produto(produto_dict)
        
        return {
            "sucesso": True,
            "mensagem": f"Produto {produto.nome} adicionado com sucesso",
            "produto_id": produto.id
        }
    except Exception as e:
        logger.error(f"Erro ao adicionar produto: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao adicionar produto: {str(e)}"
        )

@app.put("/admin/produto/{produto_id}")
async def atualizar_produto(
    produto_id: str,
    produto: ProdutoRequest,
    assistant: AssistenteVirtual = Depends(get_assistente)
):
    """Atualiza produto existente"""
    try:
        produto_dict = produto.dict()
        assistant.rag_system.atualizar_produto(produto_id, produto_dict)
        
        return {
            "sucesso": True,
            "mensagem": f"Produto {produto_id} atualizado com sucesso"
        }
    except Exception as e:
        logger.error(f"Erro ao atualizar produto: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao atualizar produto: {str(e)}"
        )

@app.delete("/admin/produto/{produto_id}")
async def remover_produto(
    produto_id: str,
    assistant: AssistenteVirtual = Depends(get_assistente)
):
    """Remove produto do sistema"""
    try:
        assistant.rag_system.remover_produto(produto_id)
        
        return {
            "sucesso": True,
            "mensagem": f"Produto {produto_id} removido com sucesso"
        }
    except Exception as e:
        logger.error(f"Erro ao remover produto: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao remover produto: {str(e)}"
        )

@app.post("/admin/reindexar")
async def reindexar_sistema(
    background_tasks: BackgroundTasks,
    assistant: AssistenteVirtual = Depends(get_assistente)
):
    """Reindexar todo o sistema RAG"""
    try:
        background_tasks.add_task(assistant.rag_system.recriar_indices)
        
        return {
            "sucesso": True,
            "mensagem": "Reindexação iniciada em background"
        }
    except Exception as e:
        logger.error(f"Erro ao iniciar reindexação: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao iniciar reindexação: {str(e)}"
        )

@app.get("/buscar")
async def buscar_produtos(
    q: str,
    categoria: Optional[str] = None,
    preco_min: Optional[float] = None,
    preco_max: Optional[float] = None,
    top_k: int = 5,
    assistant: AssistenteVirtual = Depends(get_assistente)
):
    """Endpoint direto para busca de produtos"""
    try:
        filtros = {}
        if categoria:
            filtros["categoria"] = categoria
        if preco_min:
            filtros["preco_min"] = preco_min
        if preco_max:
            filtros["preco_max"] = preco_max
        
        produtos = assistant.rag_system.buscar_produtos_avancada(
            consulta=q,
            filtros=filtros,
            top_k=top_k
        )
        
        return {
            "consulta": q,
            "filtros": filtros,
            "total_encontrados": len(produtos),
            "produtos": produtos
        }
    except Exception as e:
        logger.error(f"Erro na busca: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro na busca: {str(e)}"
        )

@app.get("/buscar/embedding")
async def buscar_por_embedding(
    q: str,
    threshold: float = 0.6,
    top_k: int = 5,
    assistant: AssistenteVirtual = Depends(get_assistente)
):
    """Endpoint para busca usando embeddings com threshold de similaridade"""
    try:
        produtos = assistant.rag_system.buscar_por_embedding(
            consulta=q,
            top_k=top_k,
            threshold=threshold
        )
        
        return {
            "consulta": q,
            "threshold": threshold,
            "total_encontrados": len(produtos),
            "produtos": produtos
        }
    except Exception as e:
        logger.error(f"Erro na busca por embedding: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro na busca por embedding: {str(e)}"
        )

@app.get("/produtos/{produto_id}/similares")
async def obter_produtos_similares(
    produto_id: str,
    top_k: int = 3,
    assistant: AssistenteVirtual = Depends(get_assistente)
):
    """Obtém produtos similares a um produto específico"""
    try:
        produtos_similares = assistant.rag_system.obter_produtos_similares_por_categoria(
            produto_id=produto_id,
            top_k=top_k
        )
        
        return {
            "produto_id": produto_id,
            "total_similares": len(produtos_similares),
            "produtos_similares": produtos_similares
        }
    except Exception as e:
        logger.error(f"Erro ao buscar produtos similares: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao buscar produtos similares: {str(e)}"
        )

async def log_interacao(
    id_sessao: str,
    mensagem: str,
    resposta: Dict[str, Any],
    contexto: Optional[Dict[str, Any]] = None
):
    """Função para logging em background"""
    try:
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "id_sessao": id_sessao,
            "mensagem": mensagem,
            "intencao": resposta.get("intencao"),
            "sucesso": resposta.get("sucesso"),
            "contexto": contexto
        }
        
        # Aqui você pode salvar em banco de dados, arquivo, etc.
        logger.info(f"Interação registrada: {log_data}")
        
    except Exception as e:
        logger.error(f"Erro ao registrar interação: {e}")

if __name__ == "__main__":
    # Configuração para desenvolvimento
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "src.api:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    ) 