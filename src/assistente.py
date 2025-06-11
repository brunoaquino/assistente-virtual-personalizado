"""
Assistente Virtual Personalizado para E-commerce
Lógica principal do sistema
"""

import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass

from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage

from .rag_system import RAGSystem
from .prompts import PromptTemplates

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class InteracaoUsuario:
    """Classe para armazenar dados da interação"""
    id_sessao: str
    mensagem: str
    intencao: str
    contexto: Dict[str, Any]
    timestamp: datetime

class AssistenteVirtual:
    """
    Assistente Virtual Principal
    Coordena todas as funcionalidades do sistema
    """
    
    def __init__(self, openai_api_key: str, pinecone_api_key: Optional[str] = None,
                 pinecone_env: str = "gcp-starter", pinecone_index: str = "assistente-ecommerce"):
        """Inicializa o assistente com as configurações necessárias"""
        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0.3,
            openai_api_key=openai_api_key
        )
        
        # Inicializa sistema RAG
        self.rag_system = RAGSystem(
            openai_api_key=openai_api_key,
            pinecone_api_key=pinecone_api_key,
            pinecone_env=pinecone_env,
            pinecone_index=pinecone_index
        )
        
        # Templates de prompt
        self.prompts = PromptTemplates()
        
        # Carrega dados
        self._carregar_dados()
        
        # Histórico de conversas por sessão
        self.historico_sessoes: Dict[str, List[InteracaoUsuario]] = {}
    
    def _carregar_dados(self):
        """Carrega dados de produtos e pedidos"""
        try:
            with open('data/produtos.json', 'r', encoding='utf-8') as f:
                self.produtos = json.load(f)
            
            with open('data/pedidos.json', 'r', encoding='utf-8') as f:
                self.pedidos = json.load(f)
                
            logger.info(f"Dados carregados: {len(self.produtos)} produtos, {len(self.pedidos)} pedidos")
        except FileNotFoundError as e:
            logger.error(f"Erro ao carregar dados: {e}")
            self.produtos = []
            self.pedidos = []
    
    def processar_mensagem(self, mensagem: str, id_sessao: str = "default") -> Dict[str, Any]:
        """
        Processa uma mensagem do usuário e retorna resposta apropriada
        
        Args:
            mensagem: Texto da mensagem do usuário
            id_sessao: ID da sessão para manter contexto
            
        Returns:
            Dict com resposta, intenção e dados adicionais
        """
        try:
            # 1. Detecta intenção
            intencao = self._detectar_intencao(mensagem)
            logger.info(f"Intenção detectada: {intencao}")
            
            # 2. Processa baseado na intenção
            resposta_dados = self._processar_por_intencao(mensagem, intencao, id_sessao)
            
            # 3. Gera resposta natural
            resposta_final = self._gerar_resposta_natural(mensagem, intencao, resposta_dados)
            
            # 4. Armazena no histórico
            self._adicionar_ao_historico(id_sessao, mensagem, intencao, resposta_dados)
            
            # 5. Adiciona conversa ao contexto RAG para aprendizado
            produtos_mencionados = []
            if resposta_dados.get("produtos"):
                produtos_mencionados = [p.get("id") for p in resposta_dados["produtos"] if p.get("id")]
            
            self.rag_system.adicionar_conversa_ao_contexto(
                mensagem_usuario=mensagem,
                resposta_assistente=resposta_final,
                produtos_mencionados=produtos_mencionados
            )
            
            return {
                "resposta": resposta_final,
                "intencao": intencao,
                "dados": resposta_dados,
                "sucesso": True
            }
            
        except Exception as e:
            logger.error(f"Erro ao processar mensagem: {e}")
            return {
                "resposta": "Desculpe, ocorreu um erro interno. Tente novamente em alguns momentos.",
                "intencao": "erro",
                "dados": {},
                "sucesso": False,
                "erro": str(e)
            }
    
    def _detectar_intencao(self, mensagem: str) -> str:
        """Detecta a intenção do usuário usando LLM"""
        prompt = self.prompts.get_prompt_deteccao_intencao()
        
        messages = [
            SystemMessage(content=prompt),
            HumanMessage(content=f"Mensagem do usuário: {mensagem}")
        ]
        
        response = self.llm.invoke(messages)
        intencao = response.content.strip().lower()
        
        # Valida intenções conhecidas
        intencoes_validas = ["busca_produtos", "consulta_pedido", "politicas", "recomendacao", "saudacao", "outro"]
        if intencao not in intencoes_validas:
            intencao = "outro"
            
        return intencao
    
    def _processar_por_intencao(self, mensagem: str, intencao: str, id_sessao: str) -> Dict[str, Any]:
        """Processa mensagem baseado na intenção detectada"""
        
        if intencao == "busca_produtos":
            return self._buscar_produtos(mensagem)
        elif intencao == "consulta_pedido":
            return self._consultar_pedido(mensagem)
        elif intencao == "politicas":
            return self._consultar_politicas(mensagem)
        elif intencao == "recomendacao":
            return self._gerar_recomendacao(mensagem, id_sessao)
        elif intencao == "saudacao":
            return {"tipo": "saudacao", "mensagem": mensagem}
        else:
            return {"tipo": "geral", "mensagem": mensagem}
    
    def _buscar_produtos(self, consulta: str) -> Dict[str, Any]:
        """Busca produtos usando RAG e filtros"""
        try:
            # Extrai critérios de busca
            criterios = self._extrair_criterios_busca(consulta)
            
            # Busca semântica usando embeddings com threshold
            produtos_similares = self.rag_system.buscar_por_embedding(
                consulta, top_k=10, threshold=0.6
            )
            
            # Aplica filtros
            produtos_filtrados = self._aplicar_filtros(produtos_similares, criterios)
            
            return {
                "tipo": "busca_produtos",
                "produtos": produtos_filtrados[:5],  # Top 5 resultados
                "criterios": criterios,
                "total_encontrados": len(produtos_filtrados)
            }
        except Exception as e:
            logger.error(f"Erro na busca de produtos: {e}")
            return {"tipo": "erro", "mensagem": "Erro na busca de produtos"}
    
    def _extrair_criterios_busca(self, consulta: str) -> Dict[str, Any]:
        """Extrai critérios de busca da consulta usando LLM"""
        prompt = self.prompts.get_prompt_extracao_criterios()
        
        messages = [
            SystemMessage(content=prompt),
            HumanMessage(content=f"Consulta: {consulta}")
        ]
        
        response = self.llm.invoke(messages)
        
        try:
            # Tenta extrair JSON da resposta
            criterios_str = response.content.strip()
            if criterios_str.startswith("```json"):
                criterios_str = criterios_str.split("```json")[1].split("```")[0]
            
            criterios = json.loads(criterios_str)
            return criterios
        except:
            # Retorna critérios vazios se falhar
            return {"categoria": None, "preco_max": None, "características": []}
    
    def _aplicar_filtros(self, produtos: List[Dict], criterios: Dict[str, Any]) -> List[Dict]:
        """Aplica filtros aos produtos encontrados"""
        produtos_filtrados = produtos.copy()
        
        # Filtro de preço
        if criterios.get("preco_max"):
            try:
                preco_max = float(criterios["preco_max"])
                produtos_filtrados = [
                    p for p in produtos_filtrados 
                    if p.get("preco", 0) <= preco_max
                ]
            except ValueError:
                pass
        
        # Filtro de categoria
        if criterios.get("categoria"):
            categoria = criterios["categoria"].lower()
            produtos_filtrados = [
                p for p in produtos_filtrados 
                if categoria in p.get("categoria", "").lower()
            ]
        
        return produtos_filtrados
    
    def _consultar_pedido(self, mensagem: str) -> Dict[str, Any]:
        """Consulta status de pedido"""
        # Extrai número do pedido
        import re
        numeros = re.findall(r'#?(\d+)', mensagem)
        
        if not numeros:
            return {
                "tipo": "consulta_pedido",
                "erro": "Número do pedido não encontrado",
                "mensagem": "Por favor, informe o número do seu pedido. Ex: #12345"
            }
        
        numero_pedido = numeros[0]
        
        # Busca pedido
        pedido = next((p for p in self.pedidos if p["pedido_id"] == numero_pedido), None)
        
        if not pedido:
            return {
                "tipo": "consulta_pedido",
                "erro": "Pedido não encontrado",
                "numero": numero_pedido
            }
        
        return {
            "tipo": "consulta_pedido",
            "pedido": pedido,
            "numero": numero_pedido
        }
    
    def _consultar_politicas(self, mensagem: str) -> Dict[str, Any]:
        """Consulta políticas da loja usando RAG"""
        try:
            resultado = self.rag_system.buscar_politicas(mensagem)
            return {
                "tipo": "politicas",
                "resposta": resultado,
                "fonte": "base_conhecimento"
            }
        except Exception as e:
            logger.error(f"Erro ao consultar políticas: {e}")
            return {
                "tipo": "erro",
                "mensagem": "Erro ao consultar políticas"
            }
    
    def _gerar_recomendacao(self, mensagem: str, id_sessao: str) -> Dict[str, Any]:
        """Gera recomendações personalizadas"""
        try:
            # Busca produtos relevantes usando embeddings
            produtos_relevantes = self.rag_system.buscar_por_embedding(
                mensagem, top_k=8, threshold=0.5
            )
            
            # Filtra por disponibilidade
            produtos_disponiveis = [
                p for p in produtos_relevantes 
                if p.get("disponivel", True)
            ]
            
            # Seleciona top 3
            recomendacoes = produtos_disponiveis[:3]
            
            return {
                "tipo": "recomendacao",
                "produtos": recomendacoes,
                "total": len(recomendacoes)
            }
        except Exception as e:
            logger.error(f"Erro ao gerar recomendações: {e}")
            return {
                "tipo": "erro",
                "mensagem": "Erro ao gerar recomendações"
            }
    
    def _gerar_resposta_natural(self, mensagem: str, intencao: str, dados: Dict[str, Any]) -> str:
        """Gera resposta natural usando LLM"""
        try:
            prompt = self.prompts.get_prompt_resposta_natural(intencao)
            
            context = f"""
            Mensagem do usuário: {mensagem}
            Intenção: {intencao}
            Dados encontrados: {json.dumps(dados, ensure_ascii=False, indent=2)}
            """
            
            messages = [
                SystemMessage(content=prompt),
                HumanMessage(content=context)
            ]
            
            response = self.llm.invoke(messages)
            return response.content.strip()
            
        except Exception as e:
            logger.error(f"Erro ao gerar resposta natural: {e}")
            return "Desculpe, não consegui processar sua solicitação no momento."
    
    def _adicionar_ao_historico(self, id_sessao: str, mensagem: str, intencao: str, dados: Dict[str, Any]):
        """Adiciona interação ao histórico da sessão"""
        if id_sessao not in self.historico_sessoes:
            self.historico_sessoes[id_sessao] = []
        
        interacao = InteracaoUsuario(
            id_sessao=id_sessao,
            mensagem=mensagem,
            intencao=intencao,
            contexto=dados,
            timestamp=datetime.now()
        )
        
        self.historico_sessoes[id_sessao].append(interacao)
        
        # Mantém apenas últimas 10 interações por sessão
        if len(self.historico_sessoes[id_sessao]) > 10:
            self.historico_sessoes[id_sessao] = self.historico_sessoes[id_sessao][-10:]
    
    def obter_historico_sessao(self, id_sessao: str) -> List[Dict]:
        """Retorna histórico de uma sessão"""
        if id_sessao not in self.historico_sessoes:
            return []
        
        return [
            {
                "mensagem": i.mensagem,
                "intencao": i.intencao,
                "timestamp": i.timestamp.isoformat()
            }
            for i in self.historico_sessoes[id_sessao]
        ]
    
    def obter_estatisticas(self) -> Dict[str, Any]:
        """Retorna estatísticas do assistente"""
        total_sessoes = len(self.historico_sessoes)
        total_interacoes = sum(len(sessao) for sessao in self.historico_sessoes.values())
        
        # Conta intenções
        contagem_intencoes = {}
        for sessao in self.historico_sessoes.values():
            for interacao in sessao:
                intencao = interacao.intencao
                contagem_intencoes[intencao] = contagem_intencoes.get(intencao, 0) + 1
        
        return {
            "total_sessoes": total_sessoes,
            "total_interacoes": total_interacoes,
            "intencoes_populares": contagem_intencoes,
            "produtos_cadastrados": len(self.produtos),
            "pedidos_sistema": len(self.pedidos)
        } 