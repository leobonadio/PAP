#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste T1 - Compressão de texto com Bit Packing
Projeto: Epistemotécnica do Processamento
Autor: Leonardo Bonadio
Versão: T1_v1
"""

import time
import math
import psutil
import os
from collections import Counter
from typing import Tuple, Optional, Any
from datetime import datetime
from config import MODO, CONFIG_BD

# ===============================
# CONFIGURAÇÃO DO TESTE
# ===============================
FICHEIRO = "texto_teste_1.txt"
ALGORITMO = "bit_packing"
VERSAO_SCRIPT = "v1"
ORIGEM = "local"
COMENTARIO_PREVIO = "Teste de compressão estrutural com bit packing"

# ===============================
# IMPORTAÇÕES CONDICIONAIS
# ===============================
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
        MODO = "teste"
else:
    BD_DISPONIVEL = False

# ===============================
# FUNÇÕES AUXILIARES
# ===============================

def calcular_entropia(dados: bytes) -> float:
    """
    Calcula a entropia de Shannon de uma sequência de bytes.
    
    Entropia = -Σ(p(x) * log2(p(x)))
    onde p(x) é a probabilidade de cada byte
    
    Retorna 0.0 para dados vazios.
    """
    if not dados:
        return 0.0
    
    contagem = Counter(dados)
    total = len(dados)
    entropia = 0.0
    
    for count in contagem.values():
        p = count / total
        if p > 0:
            entropia -= p * math.log2(p)
    
    return entropia


def calcular_redundancia(entropia_atual: float, entropia_maxima: float) -> float:
    """
    Calcula a redundância relativa dos dados.
    
    Redundância = 1 - (entropia_atual / entropia_máxima)
    
    Retorna valor entre 0 (sem redundância) e 1 (totalmente redundante).
    """
    if entropia_maxima == 0:
        return 0.0
    return max(0.0, 1.0 - (entropia_atual / entropia_maxima))


def bit_packing_texto(texto: str) -> Tuple[bytes, dict]:
    """
    Comprime texto usando bit packing:
    - Mapeia cada caracter único para um código binário mínimo
    - Agrupa os bits e converte para bytes
    
    Retorna:
        - dados comprimidos (bytes)
        - metadados (dict) contendo a tabela de codificação e informações de padding
    """
    if not texto:
        return bytes(), {"tabela": {}, "bits_por_char": 0, "padding": 0}
    
    caracteres = sorted(set(texto))
    n_chars = len(caracteres)
    bits_por_char = max(1, math.ceil(math.log2(n_chars)))
    
    tabela = {c: format(i, f"0{bits_por_char}b") for i, c in enumerate(caracteres)}
    bits = "".join(tabela[c] for c in texto)
    
    padding = (8 - len(bits) % 8) % 8
    bits += "0" * padding
    
    dados_comprimidos = bytes(int(bits[i:i+8], 2) for i in range(0, len(bits), 8))
    
    metadados = {
        "tabela": tabela,
        "bits_por_char": bits_por_char,
        "padding": padding,
        "n_caracteres_unicos": n_chars
    }
    
    return dados_comprimidos, metadados


def medir_recursos_sistema() -> dict:
    """
    Captura métricas de recursos do sistema no momento da chamada.
    """
    process = psutil.Process(os.getpid())
    cpu_times = process.cpu_times()
    mem_info = process.memory_info()
    
    return {
        "cpu_user": cpu_times.user,
        "cpu_system": cpu_times.system,
        "memoria_rss": mem_info.rss,
        "memoria_vms": mem_info.vms
    }


# ===============================
# FUNÇÕES DE BASE DE DADOS
# ===============================

def conectar_bd() -> Optional[Any]:
    """
    Estabelece conexão com a base de dados PostgreSQL.
    Retorna None se falhar.
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
            
            ext = os.path.splitext(resultados["ficheiro"])[1].lower()
            tipo_map = {".txt": "texto", ".png": "imagem", ".jpg": "imagem", 
                       ".wav": "audio", ".bin": "binario"}
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


# ===============================
# FUNÇÃO DE OUTPUT NO TERMINAL
# ===============================

def mostrar_resultados_terminal(resultados: dict):
    """
    Exibe os resultados formatados no terminal (modo teste).
    """
    print("\n" + "="*70)
    print(f"TESTE: {resultados['algoritmo'].upper()} | {resultados['ficheiro']}")
    print("="*70)
    
    print(f"\nCompressão:")
    print(f"  {resultados['tamanho_original']} bytes -> {resultados['tamanho_final']} bytes")
    print(f"  Taxa: {resultados['taxa_compressao']:.4f} | Ganho: {resultados['ganho_compressao']*100:.2f}%")
    
    print(f"\nEntropia:")
    print(f"  Inicial: {resultados['entropia_inicial']:.4f} bits/byte")
    print(f"  Final: {resultados['entropia_final']:.4f} bits/byte")
    print(f"  Variação: {resultados['variacao_entropia']:+.4f} ({resultados['variacao_entropia_relativa']*100:+.2f}%)")
    
    print(f"\nRedundância:")
    print(f"  Inicial: {resultados['redundancia_inicial']:.4f}")
    print(f"  Final: {resultados['redundancia_final']:.4f}")
    
    print(f"\nDesempenho:")
    print(f"  Tempo: {resultados['tempo_execucao_ms']:.2f} ms")
    print(f"  CPU: {resultados['cpu_utilizado']:.2f}%")
    print(f"  Memória: {resultados['memoria_utilizada']} bytes")
    
    print("\n" + "="*70 + "\n")


# ===============================
# EXECUÇÃO DO TESTE
# ===============================

def executar_teste():
    """
    Executa o teste T1 completo e retorna todas as métricas.
    """
    
    print(f"\n{'='*70}")
    print(f"Teste T1 - Bit Packing")
    print(f"Modo: {MODO.upper()} | Início: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*70}\n")
    
    # Leitura do ficheiro
    try:
        with open(FICHEIRO, "r", encoding="utf-8") as f:
            texto = f.read()
    except FileNotFoundError:
        print(f"ERRO: Ficheiro '{FICHEIRO}' não encontrado.\n")
        return None
    except Exception as e:
        print(f"ERRO ao ler ficheiro: {e}\n")
        return None
    
    if not texto:
        print("AVISO: Ficheiro vazio.\n")
        return None
    
    dados_originais = texto.encode("utf-8")
    tamanho_original = len(dados_originais)
    
    print(f"Ficheiro lido: {len(texto)} caracteres ({tamanho_original} bytes)")
    
    # Medição e compressão
    recursos_inicio = medir_recursos_sistema()
    tempo_inicio = time.perf_counter()
    
    dados_comprimidos, metadados = bit_packing_texto(texto)
    
    tempo_fim = time.perf_counter()
    recursos_fim = medir_recursos_sistema()
    
    print("Compressão concluída")
    
    # Cálculo de métricas
    tamanho_final = len(dados_comprimidos)
    taxa_compressao = tamanho_final / tamanho_original if tamanho_original > 0 else 0
    tempo_execucao = (tempo_fim - tempo_inicio) * 1000
    
    entropia_inicial = calcular_entropia(dados_originais)
    entropia_final = calcular_entropia(dados_comprimidos)
    entropia_maxima = 8.0
    
    redundancia_inicial = calcular_redundancia(entropia_inicial, entropia_maxima)
    redundancia_final = calcular_redundancia(entropia_final, entropia_maxima)
    
    variacao_entropia = entropia_final - entropia_inicial
    variacao_entropia_relativa = variacao_entropia / entropia_inicial if entropia_inicial > 0 else 0
    
    cpu_utilizado = (recursos_fim["cpu_user"] - recursos_inicio["cpu_user"]) * 100
    memoria_utilizada = recursos_fim["memoria_rss"] - recursos_inicio["memoria_rss"]
    
    resultados = {
        "ficheiro": FICHEIRO,
        "algoritmo": ALGORITMO,
        "versao_script": VERSAO_SCRIPT,
        "origem": ORIGEM,
        "comentario_previo": COMENTARIO_PREVIO,
        "timestamp": datetime.now().isoformat(),
        
        "tamanho_original": tamanho_original,
        "tamanho_final": tamanho_final,
        "taxa_compressao": taxa_compressao,
        "ganho_compressao": 1 - taxa_compressao,
        
        "entropia_inicial": entropia_inicial,
        "entropia_final": entropia_final,
        "variacao_entropia": variacao_entropia,
        "variacao_entropia_relativa": variacao_entropia_relativa,
        "redundancia_inicial": redundancia_inicial,
        "redundancia_final": redundancia_final,
        
        "tempo_execucao_ms": tempo_execucao,
        "cpu_utilizado": cpu_utilizado,
        "memoria_utilizada": memoria_utilizada,
        
        "bits_por_caracter": metadados["bits_por_char"],
        "padding_bits": metadados["padding"],
        "caracteres_unicos": metadados["n_caracteres_unicos"],
        
        "perdas_detectadas": False,
        "nivel_ruido": variacao_entropia_relativa
    }
    
    return resultados


# ===============================
# EXECUÇÃO PRINCIPAL
# ===============================

def main():
    """
    Função principal que orquestra a execução do teste.
    """
    
    resultados = executar_teste()
    
    if not resultados:
        print("Teste falhou. A terminar.\n")
        return
    
    if MODO == "bd":
        sucesso = gravar_resultados_bd(resultados)
        if not sucesso:
            print("Falha ao gravar na BD. A mostrar resultados:\n")
            mostrar_resultados_terminal(resultados)
    else:
        mostrar_resultados_terminal(resultados)
    
    print(f"Teste concluído: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")


if __name__ == "__main__":
    main()
