"""
Sistema RAG (Retrieval Augmented Generation)
Para busca vetorial de produtos e políticas
"""

import json
import os
import logging
from typing import List, Dict, Any, Optional
import numpy as np
from datetime import datetime

import faiss
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS

try:
    from pinecone import Pinecone as PineconeClient
    PINECONE_AVAILABLE = True
except ImportError:
    PINECONE_AVAILABLE = False
    logger.warning("Pinecone não está disponível. Usando apenas FAISS local.")

logger = logging.getLogger(__name__)

class RAGSystem:
    """
    Sistema de Retrieval Augmented Generation
    Gerencia embeddings e busca vetorial
    """
    
    def __init__(self, openai_api_key: str, pinecone_api_key: Optional[str] = None, 
                 pinecone_env: str = "gcp-starter", pinecone_index: str = "assistente-ecommerce"):
        """Inicializa o sistema RAG"""
        self.embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
        self.pinecone_api_key = pinecone_api_key
        self.pinecone_env = pinecone_env
        self.pinecone_index_name = pinecone_index
        self.use_pinecone = pinecone_api_key is not None and PINECONE_AVAILABLE
        
        # Stores vetoriais
        self.vector_store_produtos = None
        self.vector_store_politicas = None
        self.pinecone_index = None
        self.pinecone_client = None
        
        # Dados carregados
        self.produtos_dados = []
        self.politicas_dados = []
        
        # Inicializa Pinecone se disponível
        if self.use_pinecone:
            self._inicializar_pinecone()
        
        # Inicializa sistema
        self._inicializar_stores()
    
    def _inicializar_pinecone(self):
        """Inicializa a conexão com Pinecone"""
        try:
            if not PINECONE_AVAILABLE:
                logger.error("Pinecone não está disponível")
                return
                
            # Inicializa cliente Pinecone (nova API)
            self.pinecone_client = PineconeClient(api_key=self.pinecone_api_key)
            
            # Verifica se o índice existe
            existing_indexes = [index.name for index in self.pinecone_client.list_indexes()]
            
            if self.pinecone_index_name not in existing_indexes:
                logger.info(f"Criando índice Pinecone: {self.pinecone_index_name}")
                from pinecone import ServerlessSpec
                self.pinecone_client.create_index(
                    name=self.pinecone_index_name,
                    dimension=1536,  # Dimensão dos embeddings da OpenAI
                    metric="cosine",
                    spec=ServerlessSpec(
                        cloud="aws",
                        region="us-east-1"
                    )
                )
                
            self.pinecone_index = self.pinecone_client.Index(self.pinecone_index_name)
            logger.info(f"Pinecone inicializado: índice '{self.pinecone_index_name}'")
            
        except Exception as e:
            logger.error(f"Erro ao inicializar Pinecone: {e}")
            self.use_pinecone = False

    def _inicializar_stores(self):
        """Inicializa os stores vetoriais"""
        try:
            # Carrega produtos
            self._carregar_produtos()
            
            # Carrega políticas
            self._carregar_politicas()
            
            if self.use_pinecone:
                logger.info("Sistema RAG inicializado com Pinecone")
            else:
                logger.info("Sistema RAG inicializado com FAISS local")
            
        except Exception as e:
            logger.error(f"Erro ao inicializar RAG: {e}")
    
    def _salvar_produtos_json(self):
        """Salva produtos no arquivo JSON"""
        try:
            with open('data/produtos.json', 'w', encoding='utf-8') as f:
                json.dump(self.produtos_dados, f, ensure_ascii=False, indent=2)
            logger.info(f"Produtos salvos no arquivo JSON: {len(self.produtos_dados)} itens")
        except Exception as e:
            logger.error(f"Erro ao salvar produtos no JSON: {e}")
    
    def _carregar_produtos(self):
        """Carrega e indexa produtos"""
        try:
            # Carrega dados dos produtos
            with open('data/produtos.json', 'r', encoding='utf-8') as f:
                produtos = json.load(f)
            
            self.produtos_dados = produtos
            
            # Cria documentos para indexação
            documents = []
            for produto in produtos:
                # Cria texto para embedding
                texto_produto = self._produto_para_texto(produto)
                
                doc = Document(
                    page_content=texto_produto,
                    metadata={
                        "id": produto.get("id"),
                        "nome": produto.get("nome"),
                        "categoria": produto.get("categoria"),
                        "preco": produto.get("preco"),
                        "disponivel": produto.get("disponivel", True),
                        "tipo": "produto"
                    }
                )
                documents.append(doc)
            
            # Cria vector store
            if documents:
                if self.use_pinecone:
                    # Usa Pinecone com a nova API
                    from langchain_pinecone import PineconeVectorStore
                    self.vector_store_produtos = PineconeVectorStore.from_documents(
                        documents,
                        self.embeddings,
                        index_name=self.pinecone_index_name
                    )
                    logger.info(f"Indexados {len(documents)} produtos no Pinecone")
                else:
                    # Usa FAISS local
                    self.vector_store_produtos = FAISS.from_documents(
                        documents, 
                        self.embeddings
                    )
                    # Salva índice local
                    self.vector_store_produtos.save_local("data/faiss_produtos")
                    logger.info(f"Indexados {len(documents)} produtos no FAISS local")
            
        except FileNotFoundError:
            logger.warning("Arquivo produtos.json não encontrado")
        except Exception as e:
            logger.error(f"Erro ao carregar produtos: {e}")
    
    def _carregar_politicas(self):
        """Carrega e indexa políticas"""
        try:
            # Carrega documento de políticas
            with open('data/politicas.md', 'r', encoding='utf-8') as f:
                conteudo_politicas = f.read()
            
            # Divide em chunks
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                separators=["\n\n", "\n", ". ", " "]
            )
            
            chunks = text_splitter.split_text(conteudo_politicas)
            
            # Cria documentos
            documents = []
            for i, chunk in enumerate(chunks):
                doc = Document(
                    page_content=chunk,
                    metadata={
                        "id": f"politica_{i}",
                        "tipo": "politica",
                        "chunk_index": i
                    }
                )
                documents.append(doc)
            
            # Cria vector store
            if documents:
                if self.use_pinecone:
                    # Para políticas, adiciona prefixo no namespace ou metadata
                    for doc in documents:
                        doc.metadata["namespace"] = "politicas"
                    
                    # Usa o mesmo índice Pinecone mas com namespace diferente
                    from langchain_pinecone import PineconeVectorStore
                    self.vector_store_politicas = PineconeVectorStore.from_documents(
                        documents,
                        self.embeddings,
                        index_name=self.pinecone_index_name,
                        namespace="politicas"
                    )
                    logger.info(f"Indexados {len(documents)} chunks de políticas no Pinecone")
                else:
                    # Usa FAISS local
                    self.vector_store_politicas = FAISS.from_documents(
                        documents, 
                        self.embeddings
                    )
                    # Salva índice local
                    self.vector_store_politicas.save_local("data/faiss_politicas")
                    logger.info(f"Indexados {len(documents)} chunks de políticas no FAISS local")
                
        except FileNotFoundError:
            logger.warning("Arquivo politicas.md não encontrado")
        except Exception as e:
            logger.error(f"Erro ao carregar políticas: {e}")
    
    def _produto_para_texto(self, produto: Dict[str, Any]) -> str:
        """Converte produto em texto para embedding"""
        texto_parts = []
        
        # Nome e categoria
        if produto.get("nome"):
            texto_parts.append(f"Nome: {produto['nome']}")
        
        if produto.get("categoria"):
            texto_parts.append(f"Categoria: {produto['categoria']}")
        
        # Descrição
        if produto.get("descricao"):
            texto_parts.append(f"Descrição: {produto['descricao']}")
        
        # Preço
        if produto.get("preco"):
            texto_parts.append(f"Preço: R$ {produto['preco']:.2f}")
        
        # Especificações
        if produto.get("especificacoes"):
            specs = produto["especificacoes"]
            for key, value in specs.items():
                texto_parts.append(f"{key.title()}: {value}")
        
        # Características adicionais
        if produto.get("caracteristicas"):
            caracteristicas = produto["caracteristicas"]
            if isinstance(caracteristicas, list):
                texto_parts.append(f"Características: {', '.join(caracteristicas)}")
            elif isinstance(caracteristicas, str):
                texto_parts.append(f"Características: {caracteristicas}")
        
        # Disponibilidade
        disponivel = produto.get("disponivel", True)
        status = "Disponível" if disponivel else "Indisponível"
        texto_parts.append(f"Status: {status}")
        
        return " | ".join(texto_parts)
    
    def buscar_produtos(self, consulta: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Busca produtos usando similaridade vetorial
        
        Args:
            consulta: Texto da consulta
            top_k: Número máximo de resultados
            
        Returns:
            Lista de produtos ordenados por relevância
        """
        if not self.vector_store_produtos:
            logger.warning("Vector store de produtos não inicializado")
            return []
        
        try:
            # Busca documentos similares
            docs_e_scores = self.vector_store_produtos.similarity_search_with_score(
                consulta, k=top_k
            )
            
            # Converte para produtos
            produtos_encontrados = []
            for doc, score in docs_e_scores:
                produto_id = doc.metadata.get("id")
                
                # Encontra produto completo nos dados
                produto_completo = next(
                    (p for p in self.produtos_dados if p.get("id") == produto_id),
                    None
                )
                
                if produto_completo:
                    produto_com_score = produto_completo.copy()
                    produto_com_score["relevancia_score"] = float(score)
                    produtos_encontrados.append(produto_com_score)
            
            # Ordena por score (menor = mais similar)
            produtos_encontrados.sort(key=lambda x: x["relevancia_score"])
            
            logger.info(f"Encontrados {len(produtos_encontrados)} produtos para: {consulta}")
            return produtos_encontrados
            
        except Exception as e:
            logger.error(f"Erro na busca de produtos: {e}")
            return []
    
    def buscar_politicas(self, consulta: str, top_k: int = 3) -> str:
        """
        Busca políticas usando similaridade vetorial
        
        Args:
            consulta: Texto da consulta
            top_k: Número máximo de chunks
            
        Returns:
            Texto das políticas relevantes
        """
        if not self.vector_store_politicas:
            logger.warning("Vector store de políticas não inicializado")
            return "Políticas não disponíveis no momento."
        
        try:
            # Busca documentos similares
            docs_similares = self.vector_store_politicas.similarity_search(
                consulta, k=top_k
            )
            
            # Combina conteúdo dos chunks
            conteudo_relevante = []
            for doc in docs_similares:
                conteudo_relevante.append(doc.page_content)
            
            resultado = "\n\n".join(conteudo_relevante)
            
            logger.info(f"Encontrados {len(docs_similares)} chunks de políticas para: {consulta}")
            return resultado
            
        except Exception as e:
            logger.error(f"Erro na busca de políticas: {e}")
            return "Erro ao consultar políticas."
    
    def adicionar_produto(self, produto: Dict[str, Any]):
        """Adiciona novo produto ao índice E persiste no arquivo JSON"""
        try:
            # Adiciona aos dados em memória
            self.produtos_dados.append(produto)
            
            # Persiste no arquivo JSON
            self._salvar_produtos_json()
            
            # Cria documento com embedding
            texto_produto = self._produto_para_texto(produto)
            doc = Document(
                page_content=texto_produto,
                metadata={
                    "id": produto.get("id"),
                    "nome": produto.get("nome"),
                    "categoria": produto.get("categoria"),
                    "preco": produto.get("preco"),
                    "disponivel": produto.get("disponivel", True),
                    "tipo": "produto"
                }
            )
            
            # Adiciona ao vector store
            if self.vector_store_produtos:
                self.vector_store_produtos.add_documents([doc])
                
                if self.use_pinecone:
                    # Pinecone salva automaticamente na nuvem
                    logger.info(f"Produto adicionado ao Pinecone: {produto.get('nome')}")
                else:
                    # Salva índice FAISS local
                    self.vector_store_produtos.save_local("data/faiss_produtos")
                    logger.info(f"Produto adicionado ao FAISS local: {produto.get('nome')}")
            else:
                # Se não existe vector store, recria
                self._carregar_produtos()
            
            logger.info(f"Produto adicionado e persistido: {produto.get('nome')}")
            
        except Exception as e:
            logger.error(f"Erro ao adicionar produto: {e}")
    
    def atualizar_produto(self, produto_id: str, produto_atualizado: Dict[str, Any]):
        """Atualiza produto existente E persiste no arquivo JSON"""
        try:
            # Atualiza nos dados em memória
            produto_encontrado = False
            for i, produto in enumerate(self.produtos_dados):
                if produto.get("id") == produto_id:
                    self.produtos_dados[i] = produto_atualizado
                    produto_encontrado = True
                    break
            
            if not produto_encontrado:
                raise ValueError(f"Produto com ID {produto_id} não encontrado")
            
            # Persiste no arquivo JSON
            self._salvar_produtos_json()
            
            # Recriar o índice vetorial com os dados atualizados
            self._carregar_produtos()
            
            logger.info(f"Produto atualizado e persistido: {produto_id}")
            
        except Exception as e:
            logger.error(f"Erro ao atualizar produto: {e}")
    
    def remover_produto(self, produto_id: str):
        """Remove produto do índice E persiste no arquivo JSON"""
        try:
            # Verifica se produto existe
            produto_original = len(self.produtos_dados)
            
            # Remove dos dados em memória
            self.produtos_dados = [
                p for p in self.produtos_dados 
                if p.get("id") != produto_id
            ]
            
            if len(self.produtos_dados) == produto_original:
                raise ValueError(f"Produto com ID {produto_id} não encontrado")
            
            # Persiste no arquivo JSON
            self._salvar_produtos_json()
            
            # Remove do vector store e recria índice
            if self.use_pinecone:
                # Para Pinecone, precisamos recriar o índice pois não há delete específico no LangChain
                self._carregar_produtos()
                logger.info(f"Produto removido do Pinecone: {produto_id}")
            else:
                # Para FAISS, recria o índice
                self._carregar_produtos()
                logger.info(f"Produto removido do FAISS local: {produto_id}")
            
            logger.info(f"Produto removido e persistido: {produto_id}")
            
        except Exception as e:
            logger.error(f"Erro ao remover produto: {e}")
    
    def recriar_indices(self):
        """Recria todos os índices vetoriais"""
        try:
            logger.info("Recriando índices...")
            self._carregar_produtos()
            self._carregar_politicas()
            logger.info("Índices recriados com sucesso")
        except Exception as e:
            logger.error(f"Erro ao recriar índices: {e}")
    
    def obter_estatisticas(self) -> Dict[str, Any]:
        """Retorna estatísticas do sistema RAG"""
        stats = {
            "produtos_indexados": len(self.produtos_dados),
            "vector_store_produtos_ativo": self.vector_store_produtos is not None,
            "vector_store_politicas_ativo": self.vector_store_politicas is not None,
            "usando_pinecone": self.use_pinecone,
            "pinecone_disponivel": PINECONE_AVAILABLE,
        }
        
        if self.use_pinecone:
            # Estatísticas do Pinecone
            stats["pinecone_index_name"] = self.pinecone_index_name
            stats["pinecone_environment"] = self.pinecone_env
            stats["tipo_vector_store"] = "Pinecone (nuvem)"
            if self.pinecone_index:
                try:
                    index_stats = self.pinecone_index.describe_index_stats()
                    stats["total_vetores_pinecone"] = index_stats.get("total_vector_count", 0)
                except:
                    pass
        else:
            # Estatísticas do FAISS local
            stats["tipo_vector_store"] = "FAISS (local)"
            if self.vector_store_produtos:
                try:
                    stats["dimensao_embeddings"] = self.vector_store_produtos.index.d
                    stats["total_vetores_produtos"] = self.vector_store_produtos.index.ntotal
                except:
                    pass
        
        return stats
    
    def buscar_produtos_avancada(
        self, 
        consulta: str, 
        filtros: Dict[str, Any] = None,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Busca avançada com filtros pós-busca
        
        Args:
            consulta: Texto da consulta
            filtros: Filtros a aplicar (categoria, preco_min, preco_max, etc.)
            top_k: Número máximo de resultados
        """
        # Busca inicial mais ampla
        produtos_iniciais = self.buscar_produtos(consulta, top_k * 3)
        
        if not filtros:
            return produtos_iniciais[:top_k]
        
        # Aplica filtros
        produtos_filtrados = produtos_iniciais
        
        # Filtro de categoria
        if filtros.get("categoria"):
            categoria = filtros["categoria"].lower()
            produtos_filtrados = [
                p for p in produtos_filtrados
                if categoria in p.get("categoria", "").lower()
            ]
        
        # Filtro de preço mínimo
        if filtros.get("preco_min"):
            preco_min = float(filtros["preco_min"])
            produtos_filtrados = [
                p for p in produtos_filtrados
                if p.get("preco", 0) >= preco_min
            ]
        
        # Filtro de preço máximo
        if filtros.get("preco_max"):
            preco_max = float(filtros["preco_max"])
            produtos_filtrados = [
                p for p in produtos_filtrados
                if p.get("preco", 0) <= preco_max
            ]
        
        # Filtro de disponibilidade
        if filtros.get("apenas_disponiveis"):
            produtos_filtrados = [
                p for p in produtos_filtrados
                if p.get("disponivel", True)
            ]
        
        return produtos_filtrados[:top_k]
    
    def buscar_por_embedding(self, consulta: str, top_k: int = 5, threshold: float = 0.7) -> List[Dict[str, Any]]:
        """
        Busca avançada usando embeddings com threshold de similaridade
        
        Args:
            consulta: Texto da consulta
            top_k: Número máximo de resultados
            threshold: Threshold de similaridade (0-1, onde 1 é idêntico)
            
        Returns:
            Lista de produtos com scores de similaridade
        """
        if not self.vector_store_produtos:
            logger.warning("Vector store de produtos não inicializado")
            return []
        
        try:
            # Busca com score
            docs_com_score = self.vector_store_produtos.similarity_search_with_score(
                consulta, k=top_k * 2  # Busca mais para filtrar por threshold
            )
            
            produtos_encontrados = []
            for doc, score in docs_com_score:
                # Converte distância para similaridade (FAISS usa distância euclidiana)
                similaridade = 1.0 / (1.0 + score)
                
                if similaridade >= threshold:
                    produto_id = doc.metadata.get("id")
                    produto_completo = next(
                        (p for p in self.produtos_dados if p.get("id") == produto_id),
                        None
                    )
                    
                    if produto_completo:
                        produto_com_score = produto_completo.copy()
                        produto_com_score["similaridade_score"] = float(similaridade)
                        produto_com_score["distancia_euclidiana"] = float(score)
                        produtos_encontrados.append(produto_com_score)
            
            # Ordena por similaridade (maior = mais similar)
            produtos_encontrados.sort(key=lambda x: x["similaridade_score"], reverse=True)
            
            logger.info(f"Encontrados {len(produtos_encontrados)} produtos com similaridade >= {threshold}")
            return produtos_encontrados[:top_k]
            
        except Exception as e:
            logger.error(f"Erro na busca por embedding: {e}")
            return []
    
    def adicionar_conversa_ao_contexto(self, mensagem_usuario: str, resposta_assistente: str, 
                                       produtos_mencionados: List[str] = None):
        """
        Adiciona conversas ao contexto para melhorar recomendações futuras
        
        Args:
            mensagem_usuario: Mensagem do usuário
            resposta_assistente: Resposta do assistente
            produtos_mencionados: Lista de IDs de produtos mencionados
        """
        try:
            conversa_texto = f"Usuário: {mensagem_usuario}\nAssistente: {resposta_assistente}"
            
            # Cria documento de contexto
            doc_contexto = Document(
                page_content=conversa_texto,
                metadata={
                    "tipo": "conversa",
                    "timestamp": datetime.now().isoformat(),
                    "produtos_mencionados": produtos_mencionados or [],
                    "categoria_conversa": self._classificar_conversa(mensagem_usuario)
                }
            )
            
            # Adiciona ao vector store de produtos (pode criar um separado para conversas no futuro)
            if self.vector_store_produtos:
                self.vector_store_produtos.add_documents([doc_contexto])
                
                if not self.use_pinecone:
                    # Salva apenas se for FAISS (Pinecone salva automaticamente)
                    self.vector_store_produtos.save_local("data/faiss_produtos")
            
            if self.use_pinecone:
                logger.info("Conversa adicionada ao contexto RAG (Pinecone)")
            else:
                logger.info("Conversa adicionada ao contexto RAG (FAISS local)")
            
        except Exception as e:
            logger.error(f"Erro ao adicionar conversa ao contexto: {e}")
    
    def _classificar_conversa(self, mensagem: str) -> str:
        """Classifica o tipo de conversa baseado na mensagem"""
        mensagem_lower = mensagem.lower()
        
        if any(word in mensagem_lower for word in ["comprar", "preço", "quanto custa"]):
            return "compra"
        elif any(word in mensagem_lower for word in ["trocar", "devolver", "garantia"]):
            return "suporte"
        elif any(word in mensagem_lower for word in ["recomendar", "sugerir", "indicar"]):
            return "recomendacao"
        elif any(word in mensagem_lower for word in ["pedido", "entrega", "envio"]):
            return "logistica"
        else:
            return "geral"
    
    def obter_produtos_similares_por_categoria(self, produto_id: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Busca produtos similares baseado na categoria e características de um produto específico
        
        Args:
            produto_id: ID do produto de referência
            top_k: Número de produtos similares para retornar
            
        Returns:
            Lista de produtos similares
        """
        try:
            # Encontra o produto de referência
            produto_ref = next(
                (p for p in self.produtos_dados if p.get("id") == produto_id),
                None
            )
            
            if not produto_ref:
                logger.warning(f"Produto {produto_id} não encontrado")
                return []
            
            # Cria consulta baseada no produto
            consulta = f"{produto_ref.get('categoria', '')} {produto_ref.get('nome', '')}"
            if produto_ref.get('especificacoes'):
                specs = ' '.join(str(v) for v in produto_ref['especificacoes'].values())
                consulta += f" {specs}"
            
            # Busca produtos similares
            produtos_similares = self.buscar_por_embedding(consulta, top_k + 1)  # +1 para excluir o próprio produto
            
            # Remove o produto de referência dos resultados
            produtos_similares = [
                p for p in produtos_similares 
                if p.get("id") != produto_id
            ]
            
            return produtos_similares[:top_k]
            
        except Exception as e:
            logger.error(f"Erro ao buscar produtos similares: {e}")
            return [] 