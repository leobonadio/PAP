# Aplicação Web de Análise - Epistemotécnica

Aplicação Flask para análise crítica dos testes de compressão.

## Funcionalidades

✅ **Listar todos os testes** da base de dados
✅ **Filtrar por** algoritmo, tipo de ficheiro, origem
✅ **Comparar até 4 testes** lado a lado
✅ **Eliminar registos** da base de dados
✅ **Criar e editar reflexões** epistemotécnicas

## Instalação
```bash
pip install flask psycopg2-binary
```

## Executar
```bash
python3 run_app.py
```

Depois abrir no browser: `http://localhost:5000`

## Estrutura
```
app/
├── app.py              # Aplicação principal
├── database.py         # Queries à BD
├── templates/          # HTML
│   ├── base.html
│   ├── index.html
│   ├── comparacao.html
│   └── reflexao.html
└── static/             # CSS e JS
    ├── style.css
    └── script.js
```

## Métricas Exibidas

As métricas exibidas correspondem exatamente ao output do modo teste:

- **Compressão:** original → final, taxa, ganho
- **Entropia:** inicial, final, variação
- **Redundância:** inicial, final
- **Desempenho:** tempo, CPU, memória