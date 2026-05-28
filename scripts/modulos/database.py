#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo de Base de Dados
Funções para conexão e inserção de dados no PostgreSQL
"""

import os
from typing import Optional, Any
from datetime import datetime
from config import MODO, CONFIG_BD

# Importações condicionais do psycopg2
if MODO == "bd":
    try:
        import psycopg2
        from psycopg2 import sql
        BD_DISPONIVEL = True
    except ImportError:
        print("AVISO: psycopg2 não está instalado.")
        print("Instale com: pip install psycopg2-binary")
        print("A executar em modo 'teste' como fallback.\n")
        BD_DISPONIVEL = False
else:
    BD_DISPONIVEL = False


def conectar_bd() -> Optional[Any]:
    """
    Estabelece conexão com a base de dados PostgreSQL.
    
    Utiliza as credenciais definidas em CONFIG_BD do ficheiro config.py
    
    Returns:
        Objeto de conexão psycopg2 ou None se falhar
    """
    if not BD_DISPONIVEL:
        return None
    
    try:
        conn = psycopg2.connect(**CONFIG_BD)
        return conn
    except Exception as e:
        print(f"ERRO ao conectar à base de dados: {e}")
        print("Verifique:")
        print(f"  - O servidor está acessível em {CONFIG_BD['host']}:{CONFIG_BD['port']}")
        print(f"  - As credenciais estão corretas")
        print(f"  - O PostgreSQL está a correr no Alpine\n")
        return None


def inserir_teste_bd(conn: Any, resultados: dict) -> Optional[int]:
    """
    Insere um novo teste na tabela 'testes' e retorna o id gerado.
    
    Args:
        conn: Conexão ativa à base de dados
        resultados: Dicionário com os dados do teste
    
    Returns:
        ID do teste inserido ou None se falhar
    """
    if not BD_DISPONIVEL:
        return None
    
    try:
        with conn.cursor() as cur:
            query = psycopg2.sql.SQL("""
                INSERT INTO testes (
                    tipo_ficheiro, nome_ficheiro, tamanho_original,
                    algoritmo, versao_script, origem, data_execucao, comentario_previo
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """)
            
            # Determina tipo de ficheiro pela extensão
            ext = os.path.splitext(resultados["ficheiro"])[1].lower()
            tipo_map = {
                ".txt": "texto",
                ".png": "imagem",
                ".jpg": "imagem",
                ".jpeg": "imagem",
                ".wav": "audio",
                ".mp3": "audio",
                ".bin": "binario"
            }
            tipo_ficheiro = tipo_map.get(ext, "outro")
            
            cur.execute(query, (
                tipo_ficheiro,
                resultados["ficheiro"],
                resultados["tamanho_original"],
                resultados["algoritmo"],
                resultados["versao_script"],
                resultados["origem"],
                datetime.now(),
                resultados["comentario_previo"]
            ))
            
            id_teste = cur.fetchone()[0]
            conn.commit()
            return id_teste
            
    except Exception as e:
        print(f"ERRO ao inserir teste: {e}")
        conn.rollback()
        return None


def inserir_metricas_bd(conn: Any, id_teste: int, resultados: dict) -> bool:
    """
    Insere as métricas técnicas na tabela 'metricas_tecnicas'.
    
    Args:
        conn: Conexão ativa à base de dados
        id_teste: ID do teste ao qual as métricas pertencem
        resultados: Dicionário com as métricas calculadas
    
    Returns:
        True se inserção bem-sucedida, False caso contrário
    """
    if not BD_DISPONIVEL:
        return False
    
    try:
        with conn.cursor() as cur:
            query = psycopg2.sql.SQL("""
                INSERT INTO metricas_tecnicas (
                    id_teste, tamanho_final, taxa_compressao, tempo_execucao,
                    entropia_inicial, entropia_final, perdas_detectadas,
                    nivel_ruido, redundancia_detectada, cpu_utilizacao, memoria_utilizada
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """)
            
            cur.execute(query, (
                id_teste,
                resultados["tamanho_final"],
                resultados["taxa_compressao"],
                resultados["tempo_execucao_ms"],
                resultados["entropia_inicial"],
                resultados["entropia_final"],
                resultados["perdas_detectadas"],
                resultados["nivel_ruido"],
                resultados["redundancia_inicial"],
                resultados["cpu_utilizado"],
                resultados["memoria_utilizada"]
            ))
            
            conn.commit()
            return True
            
    except Exception as e:
        print(f"ERRO ao inserir métricas: {e}")
        conn.rollback()
        return False


def gravar_resultados_bd(resultados: dict) -> bool:
    """
    Função principal para gravar todos os resultados na base de dados.
    
    Coordena a conexão, inserção do teste e inserção das métricas.
    
    Args:
        resultados: Dicionário completo com dados do teste e métricas
    
    Returns:
        True se gravação bem-sucedida, False caso contrário
    """
    if not BD_DISPONIVEL:
        print("Base de dados não disponível\n")
        return False
    
    print("A conectar à base de dados...")
    
    conn = conectar_bd()
    if not conn:
        return False
    
    id_teste = inserir_teste_bd(conn, resultados)
    if not id_teste:
        conn.close()
        return False
    
    if not inserir_metricas_bd(conn, id_teste, resultados):
        conn.close()
        return False
    
    conn.close()
    print(f"Dados gravados com sucesso (id_teste: {id_teste})\n")
    return True