#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste T6 - Teste de consistência: 30 repetições do T2 (Gzip)
Projeto: Epistemotécnica do Processamento
Autor: Leonardo Bonadio
Versão: T6_v1
"""

import gzip
import time
from datetime import datetime
from typing import List
from config import MODO

from modulos import (
    calcular_entropia,
    calcular_redundancia,
    medir_recursos_sistema,
    gravar_resultados_bd,
    mostrar_resultados_terminal
)

# ===============================
# CONFIGURAÇÃO DO TESTE
# ===============================
FICHEIRO = "ficheiros_teste/texto_teste_1.txt"
ALGORITMO = "gzip_consistencia"
VERSAO_SCRIPT = "v1"
ORIGEM = "local"
NUM_REPETICOES = 30
COMENTARIO_PREVIO = f"Teste de consistência: {NUM_REPETICOES} repetições de compressão Gzip"

# ===============================
# EXECUÇÃO DE UMA ITERAÇÃO
# ===============================

def executar_iteracao(dados_originais: bytes, iteracao: int) -> dict:
    """
    Executa uma única iteração do teste de compressão.
    
    Args:
        dados_originais: Dados a comprimir
        iteracao: Número da iteração atual
    
    Returns:
        Dicionário com resultados desta iteração
    """
    tamanho_original = len(dados_originais)
    
    # Medição e compressão
    recursos_inicio = medir_recursos_sistema()
    tempo_inicio = time.perf_counter()
    
    dados_comprimidos = gzip.compress(dados_originais)
    
    tempo_fim = time.perf_counter()
    recursos_fim = medir_recursos_sistema()
    
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
    
    return {
        "iteracao": iteracao,
        "ficheiro": FICHEIRO,
        "algoritmo": ALGORITMO,
        "versao_script": VERSAO_SCRIPT,
        "origem": ORIGEM,
        "comentario_previo": f"{COMENTARIO_PREVIO} - Iteração {iteracao}/{NUM_REPETICOES}",
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
        
        "perdas_detectadas": False,
        "nivel_ruido": abs(variacao_entropia)
    }


# ===============================
# CÁLCULO DE MÉDIAS
# ===============================

def calcular_medias(resultados_lista: List[dict]) -> dict:
    """
    Calcula as médias de todas as métricas das iterações.
    
    Args:
        resultados_lista: Lista com resultados de todas as iterações
    
    Returns:
        Dicionário com valores médios
    """
    n = len(resultados_lista)
    
    # Soma todas as métricas
    soma = {
        "tamanho_original": 0,
        "tamanho_final": 0,
        "taxa_compressao": 0,
        "ganho_compressao": 0,
        "entropia_inicial": 0,
        "entropia_final": 0,
        "variacao_entropia": 0,
        "variacao_entropia_relativa": 0,
        "redundancia_inicial": 0,
        "redundancia_final": 0,
        "tempo_execucao_ms": 0,
        "cpu_utilizado": 0,
        "memoria_utilizada": 0,
        "nivel_ruido": 0
    }
    
    for resultado in resultados_lista:
        for chave in soma.keys():
            soma[chave] += resultado[chave]
    
    # Calcula médias
    medias = {chave: valor / n for chave, valor in soma.items()}
    
    # Adiciona metadados
    medias.update({
        "ficheiro": f"{FICHEIRO}_media",
        "algoritmo": f"{ALGORITMO}_media",
        "versao_script": VERSAO_SCRIPT,
        "origem": ORIGEM,
        "comentario_previo": f"{COMENTARIO_PREVIO} - MÉDIA de {NUM_REPETICOES} execuções",
        "timestamp": datetime.now().isoformat(),
        "perdas_detectadas": False
    })
    
    return medias


# ===============================
# EXECUÇÃO DO TESTE
# ===============================

def executar_teste():
    """
    Executa o teste T6 completo: 30 repetições + cálculo de médias.
    
    Retorna:
        Tupla (lista_resultados, resultado_medio)
    """
    
    print(f"\n{'='*70}")
    print(f"Teste T6 - Consistência ({NUM_REPETICOES} repetições)")
    print(f"Modo: {MODO.upper()} | Início: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*70}\n")
    
    # Leitura do ficheiro
    try:
        with open(FICHEIRO, "rb") as f:
            dados_originais = f.read()
    except FileNotFoundError:
        print(f"ERRO: Ficheiro '{FICHEIRO}' não encontrado.\n")
        return None, None
    except Exception as e:
        print(f"ERRO ao ler ficheiro: {e}\n")
        return None, None
    
    if not dados_originais:
        print("AVISO: Ficheiro vazio.\n")
        return None, None
    
    tamanho_original = len(dados_originais)
    print(f"Ficheiro lido: {tamanho_original} bytes")
    print(f"A executar {NUM_REPETICOES} repetições...\n")
    
    # Executa todas as iterações
    resultados_lista = []
    
    for i in range(1, NUM_REPETICOES + 1):
        print(f"Iteração {i}/{NUM_REPETICOES}...", end=" ")
        resultado = executar_iteracao(dados_originais, i)
        resultados_lista.append(resultado)
        print("OK")
    
    print(f"\nTodas as {NUM_REPETICOES} iterações concluídas")
    print("A calcular médias...")
    
    # Calcula médias
    resultado_medio = calcular_medias(resultados_lista)
    
    print("Médias calculadas")
    
    return resultados_lista, resultado_medio


# ===============================
# EXECUÇÃO PRINCIPAL
# ===============================

def main():
    """
    Função principal que orquestra a execução do teste.
    
    Grava todas as 30 iterações + a média na base de dados.
    Mostra apenas a média no terminal.
    """
    
    resultados_lista, resultado_medio = executar_teste()
    
    if not resultados_lista or not resultado_medio:
        print("Teste falhou. A terminar.\n")
        return
    
    if MODO == "bd":
        print("\nA gravar resultados na base de dados...")
        
        # Grava todas as iterações
        sucessos = 0
        for resultado in resultados_lista:
            if gravar_resultados_bd(resultado):
                sucessos += 1
        
        print(f"{sucessos}/{NUM_REPETICOES} iterações gravadas com sucesso")
        
        # Grava a média
        print("A gravar média...")
        if gravar_resultados_bd(resultado_medio):
            print("Média gravada com sucesso\n")
        else:
            print("Falha ao gravar média\n")
        
        # Mostra apenas a média no terminal
        print("="*70)
        print("RESULTADOS MÉDIOS:")
        print("="*70)
        mostrar_resultados_terminal(resultado_medio)
    
    else:
        # Modo teste: mostra apenas a média
        print("\n" + "="*70)
        print("RESULTADOS MÉDIOS:")
        print("="*70)
        mostrar_resultados_terminal(resultado_medio)
    
    print(f"Teste concluído: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")


if __name__ == "__main__":
    main()