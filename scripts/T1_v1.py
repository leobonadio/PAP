#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste T1 - Compressão de texto com Bit Packing
Projeto: Epistemotécnica do Processamento
Autor: Leonardo Bonadio
Versão: T1_v2
"""

import time
import math
from typing import Tuple
from datetime import datetime
from config import MODO

# Importa funções dos módulos
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
ALGORITMO = "bit_packing"
VERSAO_SCRIPT = "v2"
ORIGEM = "local"
COMENTARIO_PREVIO = "Teste de compressão estrutural com bit packing"

# ===============================
# FUNÇÃO ESPECÍFICA DO TESTE T1
# ===============================

def bit_packing_texto(texto: str) -> Tuple[bytes, dict]:
    """
    Comprime texto usando bit packing.
    
    Esta é a ÚNICA função específica do T1 - todo o resto é modular!
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
    
    # Cálculo de métricas (usando funções modulares)
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