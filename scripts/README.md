# Testes de Compressão - Epistemotécnica do Processamento

Projeto de Aptidão Profissional - Leonardo Bonadio

## Configuração

Editar `config.py`:

```python
MODO = "teste"  # ou "bd"

CONFIG_BD = {
    "host": "IP_DO_SERVIDOR",
    "port": 5432,
    "database": "epistemotecnica",
    "user": "leonardo",
    "password": "senha"
}
```

## Executar Testes

**Modo teste (output no terminal):**
```bash
python3 T1_v2.py
```

**Modo BD (grava no PostgreSQL):**
1. Alterar `config.py`: `MODO = "bd"`
2. Executar: `python3 T1_v2.py`

## Descrição dos Testes

| Teste | Algoritmo | Ficheiro | Objetivo |
|-------|-----------|----------|----------|
| T1 | Bit Packing | texto | Compressão estrutural |
| T2 | Gzip | texto | Compressão estatística |
| T3 | Gzip | PNG | Ficheiro já comprimido |
| T4 | Gzip | texto+ruído | 20% ruído artificial |
| T5 | Gzip | binário | Dados aleatórios |
| T6 | Gzip | texto | 30 repetições (consistência) |

## Dependências

```bash
pip install psutil psycopg2-binary
```

scripts/
│
├── config.py                    # Ficheiro de configuração  
│
├── modulos/
│   ├── __init__.py              
│   ├── metricas.py
│   ├── database.py
│   ├── output.py
│   └── manipulacao.py         
│
├── T1_v2.py                     # Bit Packing texto
├── T2_v2.py                     # Gzip texto 
├── T3_v1.py                     # Gzip imagem PNG
├── T4_v1.py                     # Gzip com ruído
├── T5_v1.py                     # Gzip ficheiro binário
├── T6_v1.py                     # Consistência (30x T2)
│
└── ficheiros_teste/             # Pasta para ficheiros de teste
    ├── texto_teste_1.txt
    ├── imagem_teste.png
    └── binario_teste.bin        # Gerado por T5