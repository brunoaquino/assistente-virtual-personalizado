#!/usr/bin/env python3
"""
TESTE COMPLETO DO ASSISTENTE VIRTUAL E-COMMERCE
Combina todos os testes em um único arquivo organizado
"""

import os
import sys
import json
import time
import requests
from typing import Dict, Any, List

# Adiciona o diretório src ao path
sys.path.append('src')

# Configuração da API
API_BASE_URL = "http://localhost:8000"

class TesteSistemaCompleto:
    """Classe principal para executar todos os testes do sistema"""
    
    def __init__(self):
        self.produtos = []
        self.pedidos = []
        self.politicas = ""
        self.api_online = False
        
    def carregar_dados(self):
        """Carrega todos os dados necessários para os testes"""
        print("📂 Carregando dados do sistema...")
        
        try:
            # Carrega produtos
            with open('data/produtos.json', 'r', encoding='utf-8') as f:
                self.produtos = json.load(f)
            print(f"✅ Produtos carregados: {len(self.produtos)} itens")
            
            # Carrega pedidos
            with open('data/pedidos.json', 'r', encoding='utf-8') as f:
                self.pedidos = json.load(f)
            print(f"✅ Pedidos carregados: {len(self.pedidos)} itens")
            
            # Carrega políticas
            with open('data/politicas.md', 'r', encoding='utf-8') as f:
                self.politicas = f.read()
            print(f"✅ Políticas carregadas: {len(self.politicas)} caracteres")
            
            return True
            
        except FileNotFoundError as e:
            print(f"❌ Erro ao carregar dados: {e}")
            return False
    
    def verificar_ambiente(self):
        """Verifica configuração do ambiente"""
        print("\n⚙️ VERIFICANDO AMBIENTE")
        print("=" * 50)
        
        # Verifica Python
        print(f"🐍 Python: {sys.version}")
        
        # Verifica variáveis de ambiente
        if os.getenv('OPENAI_API_KEY'):
            print("✅ OPENAI_API_KEY configurada")
        else:
            print("⚠️ OPENAI_API_KEY não configurada (necessária para funcionamento completo)")
        
        # Verifica arquivos essenciais
        arquivos_essenciais = [
            'src/assistente.py',
            'src/rag_system.py', 
            'src/api.py',
            'src/prompts.py',
            'data/produtos.json',
            'data/pedidos.json',
            'data/politicas.md',
            'deploy/requirements.txt'
        ]
        
        print("\n📁 Verificando arquivos essenciais:")
        for arquivo in arquivos_essenciais:
            if os.path.exists(arquivo):
                print(f"✅ {arquivo}")
            else:
                print(f"❌ {arquivo} ausente")
    
    def testar_estrutura_dados(self):
        """Testa a estrutura e integridade dos dados"""
        print("\n🔍 TESTANDO ESTRUTURA DOS DADOS")
        print("=" * 50)
        
        # Valida produtos
        if not self.produtos:
            print("❌ Nenhum produto carregado")
            return False
            
        produto_exemplo = self.produtos[0]
        campos_obrigatorios = ['id', 'nome', 'categoria', 'preco', 'descricao']
        
        print("📦 Validando estrutura de produtos:")
        for campo in campos_obrigatorios:
            if campo not in produto_exemplo:
                print(f"❌ Campo obrigatório ausente: {campo}")
                return False
            print(f"✅ Campo {campo}: OK")
        
        # Valida pedidos
        if not self.pedidos:
            print("❌ Nenhum pedido carregado")
            return False
            
        pedido_exemplo = self.pedidos[0]
        campos_pedido = ['pedido_id', 'status', 'produtos', 'data_compra']
        
        print("\n📋 Validando estrutura de pedidos:")
        for campo in campos_pedido:
            if campo not in pedido_exemplo:
                print(f"❌ Campo obrigatório ausente: {campo}")
                return False
            print(f"✅ Campo {campo}: OK")
        
        # Estatísticas dos dados
        print("\n📊 Estatísticas dos dados:")
        categorias = set(p['categoria'] for p in self.produtos)
        print(f"✅ Categorias disponíveis: {', '.join(categorias)}")
        
        status_pedidos = set(p['status'] for p in self.pedidos)
        print(f"✅ Status de pedidos: {', '.join(status_pedidos)}")
        
        # Produtos por faixa de preço
        produtos_baratos = len([p for p in self.produtos if p['preco'] < 500])
        produtos_medios = len([p for p in self.produtos if 500 <= p['preco'] < 1500])
        produtos_caros = len([p for p in self.produtos if p['preco'] >= 1500])
        
        print(f"✅ Produtos até R$ 500: {produtos_baratos}")
        print(f"✅ Produtos R$ 500-1500: {produtos_medios}")
        print(f"✅ Produtos acima R$ 1500: {produtos_caros}")
        
        return True
    
    def testar_importacoes(self):
        """Testa se todos os módulos podem ser importados"""
        print("\n📥 TESTANDO IMPORTAÇÕES")
        print("=" * 50)
        
        try:
            from src.prompts import PromptTemplates
            prompts = PromptTemplates()
            print("✅ PromptTemplates importado")
            
            # Testa alguns prompts
            prompt_intencao = prompts.get_prompt_deteccao_intencao()
            print(f"✅ Prompt de detecção de intenção: {len(prompt_intencao)} caracteres")
            
            return True
            
        except ImportError as e:
            print(f"❌ Erro na importação: {e}")
            return False
    
    def verificar_api_online(self):
        """Verifica se a API está online"""
        print("\n🏥 VERIFICANDO API")
        print("=" * 50)
        
        try:
            response = requests.get(f"{API_BASE_URL}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ API está online: {data['status']}")
                self.api_online = True
                return True
            else:
                print(f"❌ API retornou status {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            print("❌ Não foi possível conectar à API")
            print("💡 Para iniciar a API execute: uvicorn src.api:app --reload")
            return False
        except Exception as e:
            print(f"❌ Erro ao verificar API: {e}")
            return False
    
    def testar_cenarios_principais(self):
        """Testa os 5 cenários principais do assistente"""
        if not self.api_online:
            print("\n⚠️ API não está online. Pulando testes de cenários.")
            return False
            
        print("\n🎯 TESTANDO CENÁRIOS PRINCIPAIS")
        print("=" * 50)
        
        cenarios = [
            {
                "nome": "1. Busca de Produtos",
                "mensagem": "Quero um smartphone Android, tela grande, até R$ 1.500",
                "usuario_id": "user123",
                "intencao_esperada": "busca_produtos",
                "validacoes": ["smartphone", "android", "1500", "produtos"]
            },
            {
                "nome": "2. Consulta de Políticas",
                "mensagem": "Posso trocar um produto depois de 15 dias?",
                "usuario_id": "user456",
                "intencao_esperada": "politicas",
                "validacoes": ["troca", "15 dias", "política", "prazo"]
            },
            {
                "nome": "3. Status do Pedido",
                "mensagem": "Meu pedido #12345 já saiu para entrega?",
                "usuario_id": "user789",
                "intencao_esperada": "consulta_pedido",
                "validacoes": ["pedido", "12345", "entrega", "status"]
            },
            {
                "nome": "4. Recomendações",
                "mensagem": "Que presente vocês sugerem para quem gosta de cozinhar?",
                "usuario_id": "user101",
                "intencao_esperada": "recomendacao",
                "validacoes": ["presente", "cozinhar", "sugestão", "recomend"]
            },
            {
                "nome": "5. Conversa Natural",
                "mensagem": "Oi, tudo bem? Estou procurando um presente para minha mãe",
                "usuario_id": "user202",
                "intencao_esperada": "saudacao",
                "validacoes": ["olá", "oi", "presente", "mãe"]
            }
        ]
        
        resultados = []
        
        for cenario in cenarios:
            print(f"\n🧪 {cenario['nome']}")
            print(f"👤 Input: {cenario['mensagem']}")
            
            payload = {
                "mensagem": cenario['mensagem'],
                "usuario_id": cenario['usuario_id']
            }
            
            try:
                response = requests.post(
                    f"{API_BASE_URL}/chat",
                    json=payload,
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    resposta = data.get('resposta', '')
                    intencao = data.get('intencao', '')
                    tempo = data.get('tempo_processamento', 0)
                    
                    print(f"🤖 Output: {resposta[:150]}...")
                    print(f"🔍 Intenção detectada: {intencao}")
                    print(f"⏱️  Tempo de processamento: {tempo}s")
                    
                    # Validações específicas
                    validacoes_ok = 0
                    for validacao in cenario['validacoes']:
                        if validacao.lower() in resposta.lower():
                            validacoes_ok += 1
                    
                    if validacoes_ok > 0:
                        print(f"✅ Validações: {validacoes_ok}/{len(cenario['validacoes'])} termos encontrados")
                        resultado = "PASSOU"
                    else:
                        print(f"⚠️ Validações: {validacoes_ok}/{len(cenario['validacoes'])} termos encontrados")
                        resultado = "PARCIAL"
                    
                    resultados.append({
                        'cenario': cenario['nome'],
                        'status': resultado,
                        'intencao': intencao,
                        'tempo': tempo,
                        'validacoes': f"{validacoes_ok}/{len(cenario['validacoes'])}"
                    })
                    
                else:
                    print(f"❌ Erro HTTP {response.status_code}: {response.text}")
                    resultados.append({
                        'cenario': cenario['nome'],
                        'status': 'FALHOU',
                        'erro': f"HTTP {response.status_code}"
                    })
                    
            except requests.exceptions.Timeout:
                print("❌ Timeout na requisição")
                resultados.append({
                    'cenario': cenario['nome'],
                    'status': 'TIMEOUT'
                })
            except Exception as e:
                print(f"❌ Erro: {e}")
                resultados.append({
                    'cenario': cenario['nome'],
                    'status': 'ERRO',
                    'erro': str(e)
                })
            
            # Pausa entre requests
            time.sleep(2)
        
        return resultados
    
    def testar_endpoints_adicionais(self):
        """Testa endpoints adicionais da API"""
        if not self.api_online:
            return
            
        print("\n🔧 TESTANDO ENDPOINTS ADICIONAIS")
        print("=" * 50)
        
        # Teste de estatísticas
        try:
            response = requests.get(f"{API_BASE_URL}/estatisticas")
            if response.status_code == 200:
                data = response.json()
                print("✅ Endpoint /estatisticas:")
                for key, value in data.items():
                    print(f"   - {key}: {value}")
            else:
                print(f"❌ Erro em /estatisticas: {response.status_code}")
        except Exception as e:
            print(f"❌ Erro em /estatisticas: {e}")
        
        # Teste de documentação
        try:
            response = requests.get(f"{API_BASE_URL}/docs")
            if response.status_code == 200:
                print("✅ Documentação acessível em /docs")
            else:
                print(f"❌ Documentação não acessível: {response.status_code}")
        except Exception as e:
            print(f"❌ Erro ao acessar /docs: {e}")
    
    def gerar_relatorio_final(self, resultados_cenarios):
        """Gera relatório final dos testes"""
        print("\n📋 RELATÓRIO FINAL DOS TESTES")
        print("=" * 50)
        
        if resultados_cenarios:
            print("\n🎯 Resultados dos Cenários Principais:")
            passou = 0
            total = len(resultados_cenarios)
            
            for resultado in resultados_cenarios:
                status_icon = "✅" if resultado['status'] == "PASSOU" else "⚠️" if resultado['status'] == "PARCIAL" else "❌"
                print(f"{status_icon} {resultado['cenario']}: {resultado['status']}")
                
                if 'intencao' in resultado:
                    print(f"   Intenção: {resultado['intencao']}")
                if 'tempo' in resultado:
                    print(f"   Tempo: {resultado['tempo']}s")
                if 'validacoes' in resultado:
                    print(f"   Validações: {resultado['validacoes']}")
                if 'erro' in resultado:
                    print(f"   Erro: {resultado['erro']}")
                
                if resultado['status'] in ["PASSOU", "PARCIAL"]:
                    passou += 1
            
            print(f"\n📊 Resumo: {passou}/{total} cenários funcionando")
            taxa_sucesso = (passou / total) * 100 if total > 0 else 0
            print(f"📈 Taxa de sucesso: {taxa_sucesso:.1f}%")
        
        print("\n🚀 PRÓXIMOS PASSOS:")
        if not self.api_online:
            print("1. ⚡ Inicie a API: uvicorn src.api:app --reload")
        
        print("2. 🌐 Acesse a documentação: http://localhost:8000/docs")
        print("3. 🧪 Execute testes manuais via interface web")
        print("4. 📊 Monitore estatísticas: http://localhost:8000/estatisticas")
        
        if not os.getenv('OPENAI_API_KEY'):
            print("5. 🔑 Configure OPENAI_API_KEY para funcionalidade completa")
    
    def executar_todos_testes(self):
        """Executa todos os testes do sistema"""
        print("🚀 INICIANDO TESTE COMPLETO DO SISTEMA")
        print("=" * 60)
        
        # 1. Verificar ambiente
        self.verificar_ambiente()
        
        # 2. Carregar dados
        if not self.carregar_dados():
            print("❌ Falha ao carregar dados. Abortando testes.")
            return
        
        # 3. Testar estrutura dos dados
        if not self.testar_estrutura_dados():
            print("❌ Falha na validação dos dados. Abortando testes.")
            return
        
        # 4. Testar importações
        if not self.testar_importacoes():
            print("❌ Falha nas importações. Abortando testes.")
            return
        
        # 5. Verificar API
        self.verificar_api_online()
        
        # 6. Testar cenários principais
        resultados_cenarios = self.testar_cenarios_principais()
        
        # 7. Testar endpoints adicionais
        self.testar_endpoints_adicionais()
        
        # 8. Gerar relatório final
        self.gerar_relatorio_final(resultados_cenarios)
        
        print("\n🎉 TESTE COMPLETO FINALIZADO!")

def main():
    """Função principal"""
    teste = TesteSistemaCompleto()
    teste.executar_todos_testes()

if __name__ == "__main__":
    main() 