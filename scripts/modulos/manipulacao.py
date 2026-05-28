#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo de Manipulação de Dados
Funções auxiliares para introdução de ruído e geração de ficheiros
"""

import random
import string
import os


def introduzir_ruido_texto(texto: str, percentagem: float = 0.2) -> str:
    """
    Introduz ruído aleatório num texto através da inserção de caracteres.
    
    O ruído é inserido de forma uniforme ao longo do texto.
    Caracteres inseridos são ASCII imprimíveis aleatórios.
    
    Args:
        texto: Texto original
        percentagem: Percentagem de caracteres a inserir (0.0 a 1.0)
                    Exemplo: 0.2 = inserir 20% de caracteres extras
    
    Returns:
        Texto com ruído introduzido
    
    Exemplo:
        >>> introduzir_ruido_texto("Hello", 0.2)
        "He*ll@o"  # Inseriu ~20% de caracteres (1 em 5)
    """
    if not texto or percentagem <= 0:
        return texto
    
    # Converte para lista para facilitar inserção
    caracteres = list(texto)
    tamanho_original = len(caracteres)
    
    # Calcula quantos caracteres de ruído inserir
    num_ruido = int(tamanho_original * percentagem)
    
    # Conjunto de caracteres possíveis para ruído (ASCII imprimíveis)
    chars_ruido = string.ascii_letters + string.digits + string.punctuation
    
    # Posições onde inserir ruído (distribuído uniformemente)
    posicoes = sorted(random.sample(range(len(caracteres) + num_ruido), num_ruido))
    
    # Insere caracteres de ruído nas posições escolhidas
    for i, pos in enumerate(posicoes):
        caracteres.insert(pos, random.choice(chars_ruido))
    
    return ''.join(caracteres)


def gerar_ficheiro_binario(caminho: str, tamanho_kb: int = 100) -> bool:
    """
    Gera um ficheiro binário com dados aleatórios.
    
    Útil para testes de compressão em dados sem padrão definido.
    
    Args:
        caminho: Caminho completo do ficheiro a criar
        tamanho_kb: Tamanho do ficheiro em kilobytes (padrão: 100 KB)
    
    Returns:
        True se ficheiro criado com sucesso, False caso contrário
    
    Exemplo:
        >>> gerar_ficheiro_binario("teste.bin", 50)
        True  # Cria ficheiro de 50 KB com dados aleatórios
    """
    try:
        tamanho_bytes = tamanho_kb * 1024
        
        # Gera bytes aleatórios
        dados_aleatorios = os.urandom(tamanho_bytes)
        
        # Escreve no ficheiro
        with open(caminho, "wb") as f:
            f.write(dados_aleatorios)
        
        return True
        
    except Exception as e:
        print(f"ERRO ao gerar ficheiro binário: {e}")
        return False