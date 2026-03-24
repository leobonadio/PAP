#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Aplicação Flask para análise de testes de compressão
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from app.database import Database
from datetime import datetime

app = Flask(__name__)
app.secret_key = "epistemotecnica_secret_key_2025"  # Para flash messages

db = Database()


# ===============================
# ROTAS PRINCIPAIS
# ===============================

@app.route('/')
def index():
    """Página principal - lista todos os testes"""
    testes = db.listar_todos_testes()
    estatisticas = db.obter_estatisticas_gerais()
    
    # Obter valores únicos para filtros
    algoritmos = db.obter_valores_unicos('algoritmo')
    tipos_ficheiro = db.obter_valores_unicos('tipo_ficheiro')
    origens = db.obter_valores_unicos('origem')
    
    return render_template('index.html', 
                         testes=testes,
                         estatisticas=estatisticas,
                         algoritmos=algoritmos,
                         tipos_ficheiro=tipos_ficheiro,
                         origens=origens)


@app.route('/comparacao')
def comparacao():
    """Página de comparação - até 4 testes lado a lado"""
    # Obtém IDs dos testes a comparar via query string
    ids = request.args.getlist('ids')
    
    if len(ids) > 4:
        flash("Pode comparar no máximo 4 testes", "warning")
        ids = ids[:4]
    
    testes = []
    for id_teste in ids:
        teste = db.obter_teste_por_id(int(id_teste))
        if teste:
            testes.append(teste)
    
    return render_template('comparacao.html', testes=testes)


@app.route('/reflexao/<int:id_teste>', methods=['GET', 'POST'])
def reflexao(id_teste):
    """Página de criação/edição de reflexão"""
    teste = db.obter_teste_por_id(id_teste)
    
    if not teste:
        flash("Teste não encontrado", "error")
        return redirect(url_for('index'))
    
    reflexao_existente = db.obter_reflexao(id_teste)
    
    if request.method == 'POST':
        anotacao = request.form.get('anotacao', '')
        interpretacao = request.form.get('interpretacao_epistemica', '')
        contexto = request.form.get('contexto_execucao', '')
        
        if reflexao_existente:
            # Atualizar
            sucesso = db.atualizar_reflexao(
                reflexao_existente['id'],
                anotacao,
                interpretacao,
                contexto
            )
            mensagem = "Reflexão atualizada com sucesso" if sucesso else "Erro ao atualizar reflexão"
        else:
            # Criar
            sucesso = db.criar_reflexao(
                id_teste,
                anotacao,
                interpretacao,
                contexto
            )
            mensagem = "Reflexão criada com sucesso" if sucesso else "Erro ao criar reflexão"
        
        flash(mensagem, "success" if sucesso else "error")
        
        if sucesso:
            return redirect(url_for('reflexao', id_teste=id_teste))
    
    return render_template('reflexao.html', 
                         teste=teste,
                         reflexao=reflexao_existente)


# ===============================
# API ENDPOINTS (JSON)
# ===============================

@app.route('/api/filtrar', methods=['POST'])
def api_filtrar():
    """Filtra testes via API"""
    data = request.get_json()
    
    algoritmo = data.get('algoritmo')
    tipo_ficheiro = data.get('tipo_ficheiro')
    origem = data.get('origem')
    
    testes = db.filtrar_testes(algoritmo, tipo_ficheiro, origem)
    
    return jsonify({
        'success': True,
        'testes': testes
    })


@app.route('/api/eliminar/<int:id_teste>', methods=['DELETE'])
def api_eliminar(id_teste):
    """Elimina um teste via API"""
    sucesso = db.eliminar_teste(id_teste)
    
    return jsonify({
        'success': sucesso,
        'message': 'Teste eliminado com sucesso' if sucesso else 'Erro ao eliminar teste'
    })


@app.route('/api/teste/<int:id_teste>')
def api_teste(id_teste):
    """Obtém detalhes de um teste via API"""
    teste = db.obter_teste_por_id(id_teste)
    
    if teste:
        # Converte datetime para string
        if 'data_execucao' in teste and teste['data_execucao']:
            teste['data_execucao'] = teste['data_execucao'].isoformat()
        
        return jsonify({
            'success': True,
            'teste': teste
        })
    else:
        return jsonify({
            'success': False,
            'message': 'Teste não encontrado'
        }), 404


# ===============================
# FILTROS PERSONALIZADOS JINJA2
# ===============================

@app.template_filter('format_datetime')
def format_datetime(value):
    """Formata datetime para exibição"""
    if value is None:
        return ""
    if isinstance(value, str):
        value = datetime.fromisoformat(value)
    return value.strftime('%d/%m/%Y %H:%M:%S')


@app.template_filter('format_number')
def format_number(value, decimais=4):
    """Formata números com casas decimais"""
    if value is None:
        return "N/A"
    try:
        return f"{float(value):.{decimais}f}"
    except:
        return str(value)


@app.template_filter('format_bytes')
def format_bytes(bytes_value):
    """Formata bytes para KB/MB"""
    if bytes_value is None:
        return "N/A"
    
    bytes_value = int(bytes_value)
    
    if bytes_value < 1024:
        return f"{bytes_value} B"
    elif bytes_value < 1024 * 1024:
        return f"{bytes_value / 1024:.2f} KB"
    else:
        return f"{bytes_value / (1024 * 1024):.2f} MB"


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)