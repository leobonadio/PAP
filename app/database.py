#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo de acesso à base de dados para a aplicação web
"""

import psycopg2
from psycopg2.extras import RealDictCursor
from typing import List, Optional, Dict, Any
from config import CONFIG_BD


class Database:
    """Classe para gestão de conexões e queries à base de dados"""
    
    def __init__(self):
        self.config = CONFIG_BD
    
    def _get_connection(self):
        """Cria conexão à base de dados"""
        return psycopg2.connect(**self.config)
    
    # ===============================
    # CONSULTAS - TESTES
    # ===============================
    
    def listar_todos_testes(self) -> List[Dict[str, Any]]:
        """
        Lista todos os testes com suas métricas.
        
        Returns:
            Lista de dicionários com dados dos testes
        """
        try:
            with self._get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    query = """
                        SELECT 
                            t.id,
                            t.tipo_ficheiro,
                            t.nome_ficheiro,
                            t.tamanho_original,
                            t.algoritmo,
                            t.versao_script,
                            t.origem,
                            t.data_execucao,
                            t.comentario_previo,
                            m.tamanho_final,
                            m.taxa_compressao,
                            m.tempo_execucao,
                            m.entropia_inicial,
                            m.entropia_final,
                            m.perdas_detectadas,
                            m.nivel_ruido,
                            m.redundancia_detectada,
                            m.cpu_utilizacao,
                            m.memoria_utilizada
                        FROM testes t
                        LEFT JOIN metricas_tecnicas m ON t.id = m.id_teste
                        ORDER BY t.data_execucao DESC
                    """
                    cur.execute(query)
                    return cur.fetchall()
        except Exception as e:
            print(f"Erro ao listar testes: {e}")
            return []
    
    def obter_teste_por_id(self, id_teste: int) -> Optional[Dict[str, Any]]:
        """
        Obtém um teste específico pelo ID.
        
        Args:
            id_teste: ID do teste
        
        Returns:
            Dicionário com dados do teste ou None
        """
        try:
            with self._get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    query = """
                        SELECT 
                            t.*,
                            m.tamanho_final,
                            m.taxa_compressao,
                            m.tempo_execucao,
                            m.entropia_inicial,
                            m.entropia_final,
                            m.perdas_detectadas,
                            m.nivel_ruido,
                            m.redundancia_detectada,
                            m.cpu_utilizacao,
                            m.memoria_utilizada
                        FROM testes t
                        LEFT JOIN metricas_tecnicas m ON t.id = m.id_teste
                        WHERE t.id = %s
                    """
                    cur.execute(query, (id_teste,))
                    return cur.fetchone()
        except Exception as e:
            print(f"Erro ao obter teste: {e}")
            return None
    
    def filtrar_testes(self, algoritmo: Optional[str] = None, 
                      tipo_ficheiro: Optional[str] = None,
                      origem: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Filtra testes por critérios.
        
        Args:
            algoritmo: Filtrar por algoritmo
            tipo_ficheiro: Filtrar por tipo de ficheiro
            origem: Filtrar por origem
        
        Returns:
            Lista de testes filtrados
        """
        try:
            with self._get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    query = """
                        SELECT 
                            t.id,
                            t.tipo_ficheiro,
                            t.nome_ficheiro,
                            t.algoritmo,
                            t.data_execucao,
                            m.taxa_compressao,
                            m.tempo_execucao
                        FROM testes t
                        LEFT JOIN metricas_tecnicas m ON t.id = m.id_teste
                        WHERE 1=1
                    """
                    params = []
                    
                    if algoritmo:
                        query += " AND t.algoritmo = %s"
                        params.append(algoritmo)
                    
                    if tipo_ficheiro:
                        query += " AND t.tipo_ficheiro = %s"
                        params.append(tipo_ficheiro)
                    
                    if origem:
                        query += " AND t.origem = %s"
                        params.append(origem)
                    
                    query += " ORDER BY t.data_execucao DESC"
                    
                    cur.execute(query, params)
                    return cur.fetchall()
        except Exception as e:
            print(f"Erro ao filtrar testes: {e}")
            return []
    
    def obter_valores_unicos(self, campo: str) -> List[str]:
        """
        Obtém valores únicos de um campo da tabela testes.
        
        Args:
            campo: Nome do campo (algoritmo, tipo_ficheiro, origem)
        
        Returns:
            Lista de valores únicos
        """
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    query = f"SELECT DISTINCT {campo} FROM testes ORDER BY {campo}"
                    cur.execute(query)
                    return [row[0] for row in cur.fetchall() if row[0]]
        except Exception as e:
            print(f"Erro ao obter valores únicos: {e}")
            return []
    
    # ===============================
    # CONSULTAS - REFLEXÕES
    # ===============================
    
    def obter_reflexao(self, id_teste: int) -> Optional[Dict[str, Any]]:
        """
        Obtém a reflexão associada a um teste.
        
        Args:
            id_teste: ID do teste
        
        Returns:
            Dicionário com dados da reflexão ou None
        """
        try:
            with self._get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    query = """
                        SELECT * FROM reflexoes
                        WHERE id_teste = %s
                    """
                    cur.execute(query, (id_teste,))
                    return cur.fetchone()
        except Exception as e:
            print(f"Erro ao obter reflexão: {e}")
            return None
    
    def criar_reflexao(self, id_teste: int, anotacao: str, 
                      interpretacao_epistemica: str = "",
                      contexto_execucao: str = "") -> bool:
        """
        Cria uma nova reflexão para um teste.
        
        Args:
            id_teste: ID do teste
            anotacao: Anotação principal
            interpretacao_epistemica: Interpretação epistemotécnica
            contexto_execucao: Contexto da execução
        
        Returns:
            True se criado com sucesso
        """
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    query = """
                        INSERT INTO reflexoes 
                        (id_teste, anotacao, interpretacao_epistemica, contexto_execucao)
                        VALUES (%s, %s, %s, %s)
                    """
                    cur.execute(query, (id_teste, anotacao, 
                                      interpretacao_epistemica, 
                                      contexto_execucao))
                    conn.commit()
                    return True
        except Exception as e:
            print(f"Erro ao criar reflexão: {e}")
            return False
    
    def atualizar_reflexao(self, id_reflexao: int, anotacao: str,
                          interpretacao_epistemica: str = "",
                          contexto_execucao: str = "") -> bool:
        """
        Atualiza uma reflexão existente.
        
        Args:
            id_reflexao: ID da reflexão
            anotacao: Nova anotação
            interpretacao_epistemica: Nova interpretação
            contexto_execucao: Novo contexto
        
        Returns:
            True se atualizado com sucesso
        """
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    query = """
                        UPDATE reflexoes
                        SET anotacao = %s,
                            interpretacao_epistemica = %s,
                            contexto_execucao = %s
                        WHERE id = %s
                    """
                    cur.execute(query, (anotacao, interpretacao_epistemica,
                                      contexto_execucao, id_reflexao))
                    conn.commit()
                    return True
        except Exception as e:
            print(f"Erro ao atualizar reflexão: {e}")
            return False
    
    # ===============================
    # ELIMINAÇÃO
    # ===============================
    
    def eliminar_teste(self, id_teste: int) -> bool:
        """
        Elimina um teste e suas métricas/reflexões associadas.
        
        Args:
            id_teste: ID do teste a eliminar
        
        Returns:
            True se eliminado com sucesso
        """
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    # Elimina reflexões
                    cur.execute("DELETE FROM reflexoes WHERE id_teste = %s", (id_teste,))
                    
                    # Elimina métricas
                    cur.execute("DELETE FROM metricas_tecnicas WHERE id_teste = %s", (id_teste,))
                    
                    # Elimina teste
                    cur.execute("DELETE FROM testes WHERE id = %s", (id_teste,))
                    
                    conn.commit()
                    return True
        except Exception as e:
            print(f"Erro ao eliminar teste: {e}")
            return False
    
    # ===============================
    # ESTATÍSTICAS
    # ===============================
    
    def obter_estatisticas_gerais(self) -> Dict[str, Any]:
        """
        Obtém estatísticas gerais dos testes.
        
        Returns:
            Dicionário com estatísticas
        """
        try:
            with self._get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    query = """
                        SELECT 
                            COUNT(*) as total_testes,
                            COUNT(DISTINCT algoritmo) as total_algoritmos,
                            AVG(m.taxa_compressao) as media_taxa_compressao,
                            AVG(m.tempo_execucao) as media_tempo_execucao,
                            AVG(m.entropia_inicial) as media_entropia_inicial,
                            AVG(m.entropia_final) as media_entropia_final
                        FROM testes t
                        LEFT JOIN metricas_tecnicas m ON t.id = m.id_teste
                    """
                    cur.execute(query)
                    return cur.fetchone()
        except Exception as e:
            print(f"Erro ao obter estatísticas: {e}")
            return {}