#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo de Métricas
Funções para cálculo de entropia, redundância e medição de recursos do sistema
"""

import math
import psutil
import os
from collections import Counter


def calcular_entropia(dados: bytes) -> float:
    """
    Calcula a entropia de Shannon de uma sequência de bytes.
    
    Entropia = -Σ(p(x) * log2(p(x)))
    onde p(x) é a probabilidade de cada byte
    
    Args:
        dados: Sequência de bytes a analisar
    
    Returns:
        Entropia em bits/byte. Retorna 0.0 para dados vazios.
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
    
    Args:
        entropia_atual: Entropia medida dos dados
        entropia_maxima: Entropia máxima teórica (geralmente 8.0 para bytes)
    
    Returns:
        Valor entre 0 (sem redundância) e 1 (totalmente redundante)
    """
    if entropia_maxima == 0:
        return 0.0
    return max(0.0, 1.0 - (entropia_atual / entropia_maxima))


def medir_recursos_sistema() -> dict:
    """
    Captura métricas de recursos do sistema no momento da chamada.
    
    Mede o uso de CPU e memória do processo atual.
    
    Returns:
        Dicionário com métricas de CPU (user, system) e memória (rss, vms)
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