#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo de Output
Funções para exibição formatada de resultados no terminal
"""


def mostrar_resultados_terminal(resultados: dict):
    """
    Exibe os resultados formatados no terminal (modo teste).
    
    Apresenta de forma estruturada:
    - Informações de compressão (tamanhos e taxas)
    - Métricas de entropia
    - Métricas de redundância
    - Métricas de desempenho (tempo, CPU, memória)
    
    Args:
        resultados: Dicionário completo com todas as métricas do teste
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