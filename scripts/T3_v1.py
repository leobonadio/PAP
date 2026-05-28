#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste T3 - Compressão de imagem PNG com Gzip
Projeto: Epistemotécnica do Processamento
Autor: Leonardo Bonadio
Versão: T3_v1
"""

import gzip
import time
from datetime import datetime
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
FICHEIRO = "ficheiros_teste/imagem_teste.png"
ALGORITMO = "gzip"
VERSAO_SCRIPT = "v1"
ORIGEM = "local"
COMENTARIO_PREVIO = "Teste de compressão Gzip em imagem PNG (já comprimida)"

# ===============================
# EXECUÇÃO DO TESTE
# ===============================

def executar_teste():
    """
    Executa o teste T3 completo e retorna todas as métricas.
    
    Este teste analisa o comportamento do Gzip ao comprimir uma imagem PNG,
    que já possui compressão interna. Espera-se baixa taxa de compressão
    adicional, revelando os limites da redundância detetável.
    """
    
    print(f"\n{'='*70}")
    print(f"Teste T3 - Gzip em Imagem PNG")
    print(f"Modo: {MODO.upper()} | Início: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*70}\n")
    
    # Leitura do ficheiro
    try:
        with open(FICHEIRO, "rb") as f:
            dados_originais = f.read()
    except FileNotFoundError:
        print(f"ERRO: Ficheiro '{FICHEIRO}' não encontrado.\n")
        return None
    except Exception as e:
        print(f"ERRO ao ler ficheiro: {e}\n")
        return None
    
    if not dados_originais:
        print("AVISO: Ficheiro vazio.\n")
        return None
    
    tamanho_original = len(dados_originais)
    
    print(f"Ficheiro lido: {tamanho_original} bytes")
    
    # Medição e compressão
    recursos_inicio = medir_recursos_sistema()
    tempo_inicio = time.perf_counter()
    
    dados_comprimidos = gzip.compress(dados_originais)
    
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
        
        "perdas_detectadas": False,
        "nivel_ruido": abs(variacao_entropia)
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