"""
Módulo utils - Funções partilhadas entre testes
Projeto: Epistemotécnica do Processamento
"""

from .metricas import calcular_entropia, calcular_redundancia, medir_recursos_sistema
from .database import conectar_bd, inserir_teste_bd, inserir_metricas_bd, gravar_resultados_bd
from .output import mostrar_resultados_terminal
from .manipulacao import introduzir_ruido_texto, gerar_ficheiro_binario

__all__ = [
    'calcular_entropia',
    'calcular_redundancia',
    'medir_recursos_sistema',
    'conectar_bd',
    'inserir_teste_bd',
    'inserir_metricas_bd',
    'gravar_resultados_bd',
    'mostrar_resultados_terminal',
    'introduzir_ruido_texto',
    'gerar_ficheiro_binario'
]