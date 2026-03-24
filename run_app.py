#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para iniciar a aplicação web de análise
"""

import sys
import os

# Adiciona o diretório pai ao path para imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.app import app

if __name__ == '__main__':
    print("="*70)
    print("APLICAÇÃO WEB DE ANÁLISE - EPISTEMOTÉCNICA")
    print("="*70)
    print("\nAplicação iniciada em: http://localhost:5000")
    print("\nPressione CTRL+C para terminar\n")
    print("="*70)
    
    app.run(debug=True, host='0.0.0.0', port=5000)