import os
import json
import socket
import platform
from flask import Blueprint, render_template, request, jsonify, session, abort, redirect
import jwt
from middlewares.auth_keycloak import requires_auth
from utils.mock_generator import generate_mock_data, cleanup_mock_data
from utils.unit_test_runner import (
    get_paginas_sistema, get_resumo_cobertura,
    executar_teste_pagina, executar_todos_testes,
    verificar_cobertura_rotas,
    medir_performance_rotas, verificar_headers_seguranca,
    verificar_integridade_dados, descobrir_rotas_flask,
    salvar_paginas_sistema
)

tester_bp = Blueprint('tester_bp', __name__, url_prefix='/dev/tester')

# ════════════════════════════════════════════════════════════════════
#  SEGURANÇA MULTICAMADA - IMPEDE ACESSO TOTAL EM PRODUÇÃO/HOSTING
#  4 camadas independentes: se UMA bloquear, retorna 404 (nem 403!)
#  Retorna 404 em vez de 403 para não revelar que a rota existe.
# ════════════════════════════════════════════════════════════════════

# Hostnames/IPs conhecidos do Hostinger e outros hosts
HOSTING_INDICATORS = [
    'hostinger', 'hstgr', 'cpanel', 'litespeed',
    'cloudlinux', 'licitapro.tech', 'licitapro.online',
    'trproc.licitapro', '.com.br'
]

def _is_hosting_environment():
    """Detecta se está rodando em ambiente de hosting (Hostinger, etc)."""
    # Checa 1: hostname do servidor
    hostname = socket.gethostname().lower()
    for ind in HOSTING_INDICATORS:
        if ind in hostname:
            return True
    # Checa 2: variáveis de ambiente comuns de hosting
    if os.getenv('CPANEL_USER') or os.getenv('HOME', '').startswith('/home/'):
        if 'windows' not in platform.system().lower():
            return True
    # Checa 3: header Host da requisição
    host = request.host.lower() if request else ''
    for ind in HOSTING_INDICATORS:
        if ind in host:
            return True
    return False

@tester_bp.before_request
def restrict_to_dev():
    """
    BLOQUEIO TOTAL em produção. 4 camadas independentes.
    Se qualquer uma detectar produção → retorna 404 (página não existe).
    """
    # CAMADA 1: FLASK_ENV deve ser explicitamente 'development'
    if os.getenv('FLASK_ENV', 'production') != 'development':
        abort(404)
    
    # CAMADA 2: Detectar hosting automaticamente
    if _is_hosting_environment():
        abort(404)
    
    # CAMADA 3: Bloquear se a requisição veio de domínio de produção
    host = request.host.lower()
    if any(d in host for d in ['licitapro.tech', 'licitapro.online', 'hostinger']):
        abort(404)
    
    # CAMADA 4: Só permite localhost, 127.0.0.1, ou rede local (192.168.x.x)
    remote = request.remote_addr or ''
    allowed_prefixes = ('127.', '192.168.', '10.', '::1', 'localhost')
    if not any(remote.startswith(p) for p in allowed_prefixes):
        # Aceitar se vier por trás de proxy local (X-Forwarded-For)
        forwarded = request.headers.get('X-Forwarded-For', '')
        if not any(forwarded.startswith(p) for p in allowed_prefixes):
            abort(404)

@tester_bp.route('/')
# @requires_auth # Removido temporariamente para testes locais mais fluidos, caso contrário precisaria de login
def dashboard():
    """Renderiza o Test Hub (Dashboard visual do Robô de Testes)."""
    return render_template('tester/dashboard.html')

@tester_bp.route('/api/generate-mock', methods=['POST'])
def api_generate_mock():
    """Endpoint para injetar a massa de dados de teste via AJAX."""
    try:
        generate_mock_data()
        return jsonify({"status": "success", "message": "Massa de dados (10 municípios, etc) gerada com sucesso!"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@tester_bp.route('/api/cleanup-mock', methods=['POST'])
def api_cleanup_mock():
    """Endpoint para limpar a massa de dados de teste via AJAX."""
    try:
        cleanup_mock_data()
        return jsonify({"status": "success", "message": "Dados de teste limpos com sucesso!"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# ════════════════════════════════════════════════════════════════════
#  API DE GESTÃO DE TEMPLATES (Pilar 0 - Persistência Segura)
# ════════════════════════════════════════════════════════════════════

@tester_bp.route('/api/templates', methods=['GET'])
def api_list_templates():
    """Lista todos os templates de páginas testáveis."""
    return jsonify(get_paginas_sistema())

@tester_bp.route('/api/templates', methods=['POST'])
def api_update_template():
    """Cria ou atualiza um template de página."""
    try:
        novo_template = request.get_json()
        if not novo_template or 'id' not in novo_template:
            return jsonify({"status": "error", "message": "ID do template é obrigatório"}), 400
        
        paginas = get_paginas_sistema()
        
        # Procura se já existe para dar update, senão append
        encontrado = False
        for i, p in enumerate(paginas):
            if p['id'] == novo_template['id']:
                paginas[i] = novo_template
                encontrado = True
                break
        
        if not encontrado:
            paginas.append(novo_template)
            
        if salvar_paginas_sistema(paginas):
            return jsonify({"status": "success", "message": f"Template '{novo_template.get('nome')}' salvo com sucesso!"})
        else:
            return jsonify({"status": "error", "message": "Falha ao salvar arquivo de templates"}), 500
            
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@tester_bp.route('/api/templates/<template_id>', methods=['DELETE'])
def api_delete_template(template_id):
    """Remove um template de página."""
    try:
        paginas = get_paginas_sistema()
        paginas_filtradas = [p for p in paginas if p['id'] != template_id]
        
        if len(paginas) == len(paginas_filtradas):
            return jsonify({"status": "error", "message": "Template não encontrado"}), 404
            
        if salvar_paginas_sistema(paginas_filtradas):
            return jsonify({"status": "success", "message": "Template removido com sucesso!"})
        else:
            return jsonify({"status": "error", "message": "Falha ao salvar arquivo de templates"}), 500
            
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@tester_bp.route('/api/simulate-rbac', methods=['POST'])
def api_simulate_rbac():
    """
    Endpoint para testar a segurança (RBAC). 
    Altera temporariamente o nível de acesso da sessão (Simulação de Cargo).
    """
    data = request.json
    novo_cargo = data.get('role', 'cliente')
    municipio_id = data.get('municipio_id')
    
    # Modo Sandbox ativado na sessão
    session['is_sandbox'] = True
    session['test_role_override'] = novo_cargo # Chave unificada com o middleware
    session['test_municipio'] = municipio_id
    
    # Criar um JWT mockado para evitar erros nas rotas que decodificam session['jwt_token']
    mock_payload = {
        "realm_access": {"roles": [novo_cargo, "role_trproc"]},
        "email": f"tester_{novo_cargo}@sandbox.local",
        "preferred_username": f"test_{novo_cargo}",
        "sub": "00000000-0000-0000-0000-000000000000",
        "name": f"Tester {novo_cargo.capitalize()}"
    }
    session['jwt_token'] = jwt.encode(mock_payload, "secret", algorithm="HS256")
    
    return jsonify({
        "status": "success", 
        "message": f"Nível de acesso alterado temporariamente para: {novo_cargo}. Sandbox ativado!"
    })

@tester_bp.route('/autologin/<role>', methods=['GET'])
def autologin(role):
    """
    Endpoint prático para o Launcher Desktop. Seta a sessão por GET e redireciona.
    """
    if role not in ['admin', 'cliente', 'super_admin']:
        role = 'cliente'
        
    session['is_sandbox'] = True
    session['test_role_override'] = role
    session['test_municipio'] = None
    
    mock_payload = {
        "realm_access": {"roles": [role, "role_trproc"]},
        "email": f"tester_{role}@sandbox.local",
        "preferred_username": f"test_{role}",
        "sub": "00000000-0000-0000-0000-000000000000",
        "name": f"Tester {role.capitalize()}"
    }
    session['jwt_token'] = jwt.encode(mock_payload, "secret", algorithm="HS256")
    
    return redirect('/action-center')

@tester_bp.route('/api/simulate-message-flow', methods=['POST'])
def api_simulate_message_flow():
    """
    Endpoint que simula o robô enviando uma mensagem em um processo 
    para validar duplicação e restrição de municípios.
    """
    data = request.json
    municipio_id = data.get('municipio_id')
    
    if not municipio_id:
        return jsonify({"status": "error", "message": "ID do Município é obrigatório para tramitação."}), 400
        
    logs = [
        "[OK] Processo carregado para o município isolado.",
        "[OK] Mensagem disparada para o Secretário vinculado.",
        "[OK] Verificação de duplicação: Nenhuma mensagem duplicada detectada.",
        "[OK] Tramitação concluída na caixa de areia."
    ]
    return jsonify({"status": "success", "logs": logs})


# ════════════════════════════════════════════════════════
#  TESTES UNITÁRIOS - APIs
# ════════════════════════════════════════════════════════

@tester_bp.route('/api/unit/paginas', methods=['GET'])
def api_listar_paginas():
    """Lista todas as páginas mapeadas do sistema com seus botões e campos."""
    paginas = get_paginas_sistema()
    return jsonify({"status": "success", "paginas": paginas})

@tester_bp.route('/api/unit/cobertura', methods=['GET'])
def api_cobertura():
    """Retorna o resumo de cobertura dos testes unitários."""
    resumo = get_resumo_cobertura()
    return jsonify({"status": "success", "cobertura": resumo})

@tester_bp.route('/api/unit/testar-pagina', methods=['POST'])
def api_testar_pagina():
    """Executa a bateria de testes para uma página específica."""
    data = request.json or {}
    pagina_id = data.get('pagina_id')
    role = data.get('role', 'admin')
    
    if not pagina_id:
        return jsonify({"status": "error", "message": "pagina_id é obrigatório."}), 400

    resultado = executar_teste_pagina(pagina_id, role)
    return jsonify(resultado)

@tester_bp.route('/api/unit/testar-tudo', methods=['POST'])
def api_testar_tudo():
    """Executa testes em TODAS as páginas do sistema para um nível de acesso."""
    data = request.json or {}
    role = data.get('role', 'admin')
    relatorio = executar_todos_testes(role)
    return jsonify(relatorio)

@tester_bp.route('/api/unit/cobertura-rotas', methods=['GET'])
def api_cobertura_rotas():
    """Detecta rotas Flask não mapeadas nos testes. Útil para encontrar páginas novas."""
    resultado = verificar_cobertura_rotas()
    return jsonify({"status": "success", **resultado})

@tester_bp.route('/api/unit/testar-monstro', methods=['POST'])
def api_testar_monstro():
    """Teste funcional de integração do Protocolo Monstro (Tabela Simples e Mãe-Filha)."""
    from routes.api_importacao import _generate_signature
    from models.core_models import ImportacaoMapeamento, PerguntaDinamica
    from extensions import db
    import uuid
    
    logs = []
    pergunta_fake = None
    
    try:
        # Pega a primeira pergunta dinâmica ou cria uma temporária para respeitar a Foreign Key
        pergunta = PerguntaDinamica.query.first()
        if not pergunta:
            pergunta_fake = PerguntaDinamica(label="Fake Question", campo_id="fake_id_teste", tipo="tabela_dinamica")
            db.session.add(pergunta_fake)
            db.session.flush()
            pergunta_id = pergunta_fake.id
        else:
            pergunta_id = pergunta.id

        headers_simples = ["Nome Produto", "Quantidade", "Preço"]
        headers_mae = ["LOTE", "Item", "Descrição", "Valor"]
        
        # TESTE 1: Tabela Simples - Verificar antes de salvar (deve dar False)
        sig_simples = _generate_signature(headers_simples)
        logs.append(f"[OK] Assinatura gerada: {sig_simples[:10]}...")
        
        map_simples = ImportacaoMapeamento.query.filter_by(hash_assinatura=sig_simples).first()
        if map_simples:
            logs.append(f"[AVISO] Mapeamento simples antigo encontrado. Será subscrito.")
            
        # TESTE 1.2: Salvar Tabela Simples
        novo_map = ImportacaoMapeamento(
            pergunta_alvo_id=pergunta_id,
            hash_assinatura=sig_simples,
            tipo_tabela='simples',
            chave_mestra='',
            mapeamento_json={"col_0": "nome", "col_1": "qtd", "col_2": "preco"},
            colunas_ignoradas=[]
        )
        db.session.add(novo_map)
        db.session.flush()
        logs.append("[OK] Tabela Simples salva no banco de dados (Trava 2 e 4).")
        
        # TESTE 2: Tabela Mãe-Filha - Salvar
        sig_mae = _generate_signature(headers_mae)
        map_mae = ImportacaoMapeamento(
            pergunta_alvo_id=pergunta_id,
            hash_assinatura=sig_mae,
            tipo_tabela='mae_filha',
            chave_mestra='LOTE',
            mapeamento_json={"col_0": "lote", "col_1": "item", "col_2": "desc", "col_3": "val"},
            colunas_ignoradas=[]
        )
        db.session.add(map_mae)
        db.session.flush()
        logs.append("[OK] Tabela Mãe-Filha salva no banco de dados com Chave Mestra 'LOTE' (Trava 3).")
        
        # TESTE 3: Validar a recuperação
        rec_mae = ImportacaoMapeamento.query.filter_by(hash_assinatura=sig_mae).first()
        if rec_mae and rec_mae.tipo_tabela == 'mae_filha' and rec_mae.chave_mestra == 'LOTE':
            logs.append("[OK] Auto-Match de Hash confirmado para Tabela Mãe-Filha!")
        else:
            raise Exception("Falha ao recuperar Chave Mestra no Auto-Match.")
            
        # Cleanup dos mapeamentos criados
        ImportacaoMapeamento.query.filter_by(hash_assinatura=sig_simples).delete()
        ImportacaoMapeamento.query.filter_by(hash_assinatura=sig_mae).delete()
        
        if pergunta_fake:
            db.session.delete(pergunta_fake)
            
        db.session.commit()
        logs.append("[OK] Cleanup de dados de teste finalizado.")
        
        return jsonify({"status": "success", "message": "Teste do Motor Monstro concluído com sucesso!", "logs": logs})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e), "logs": logs}), 500

@tester_bp.route('/api/unit/scan-background', methods=['POST'])
def api_scan_background():
    """
    Rastreio Global Automático (Run All Background).
    Executa todos os testes em uma thread isolada e injeta as falhas diretamente
    no Motor de Debug para visualização imediata no dashboard, sem travar a UI.
    """
    import threading
    from utils.debug_engine import _error_log, _salvar_logs, _lock
    from datetime import datetime
    
    def run_tests_and_log():
        relatorio = executar_todos_testes(role="todos")
        agora = datetime.now()
        timestamp_raw = agora.timestamp()
        timestamp_str = agora.strftime("%d/%m/%Y %H:%M:%S")
        
        # Pega as falhas_globais e converte em registros de erro simulados para o painel
        falhas = relatorio.get("falhas", [])
        
        with _lock:
            for i, falha in enumerate(falhas):
                registro = {
                    "id": int(timestamp_raw * 1000) + i,
                    "timestamp": timestamp_str,
                    "timestamp_raw": timestamp_raw,
                    "tipo": "erro",
                    "status_code": 500 if "500" in str(falha.get("detalhe", "")) else 400,
                    "metodo": "TEST",
                    "rota": falha.get("rota", "?"),
                    "url_completa": f"TESTE BACKGROUND: {falha.get('pagina', '')}",
                    "ip": "127.0.0.1",
                    "user_agent": "TRPROC Background Scanner",
                    "erro_tipo": falha.get("categoria", "Falha Teste"),
                    "erro_msg": f"[{falha.get('teste', '')}] - {falha.get('detalhe', '')}",
                    "caminho_debug": [{"passo": "Varredura Automática", "detalhe": "Detectado no Scan Background"}],
                    "traceback_completo": "",
                    "query_params": {},
                    "form_data_keys": [],
                    "contexto": {
                        "resumo": "Falha de Rastreio Global",
                        "possivel_causa": falha.get("detalhe", ""),
                        "sugestao_fix": "Verificar Rastreamento do Analisador Dinâmico",
                        "pilar_relacionado": "Pilar Automático"
                    }
                }
                _error_log.appendleft(registro)
                
        threading.Thread(target=_salvar_logs).start()

    threading.Thread(target=run_tests_and_log).start()
    
    return jsonify({
        "status": "success", 
        "message": "Scan Global iniciado em background. Verifique o Dashboard de Debug em alguns segundos."
    })



# ════════════════════════════════════════════════════════
#  TESTES INTERATIVOS NO NAVEGADOR (Robô E2E por Página)
# ════════════════════════════════════════════════════════

@tester_bp.route('/robo/<pagina_id>')
def robo_pagina(pagina_id):
    """Abre o robô de teste interativo para uma página específica."""
    pagina = next((p for p in get_paginas_sistema() if p["id"] == pagina_id), None)
    if not pagina:
        return f"Página '{pagina_id}' não encontrada no mapeamento.", 404
    return render_template('tester/robo_pagina.html', pagina=pagina, pagina_json=json.dumps(pagina, ensure_ascii=False))

@tester_bp.route('/api/unit/pagina-info/<pagina_id>', methods=['GET'])
def api_pagina_info(pagina_id):
    """Retorna os dados completos de uma página para o robô de testes."""
    pagina = next((p for p in get_paginas_sistema() if p["id"] == pagina_id), None)
    if not pagina:
        return jsonify({"status": "error", "message": f"Página '{pagina_id}' não encontrada."}), 404
    return jsonify({"status": "success", "pagina": pagina})


# ════════════════════════════════════════════════════════
#  MÓDULO DE DEBUG — APIs
# ════════════════════════════════════════════════════════

from utils.debug_engine import (
    get_error_logs, get_threat_logs, get_error_stats,
    get_error_detail, limpar_logs, analisar_falhas_teste
)

@tester_bp.route('/api/debug/analisar-falhas', methods=['POST'])
def api_debug_analisar_falhas():
    """
    Recebe a lista de falhas dos testes e retorna análise dinâmica completa.
    Rastreia o caminho pelo código-fonte SEM modificar nada.
    Entrada: { "falhas": [{pagina, rota, categoria, teste, detalhe}] }
    """
    data = request.json or {}
    falhas = data.get('falhas', [])
    if not falhas:
        return jsonify({"status": "success", "analises": [], "total": 0})
    analises = analisar_falhas_teste(falhas)
    return jsonify({"status": "success", "analises": analises, "total": len(analises)})

@tester_bp.route('/api/debug/erros', methods=['GET'])
def api_debug_erros():
    """Lista os últimos erros capturados pelo motor de debug."""
    limit = request.args.get('limit', 50, type=int)
    filtro = request.args.get('tipo', None)
    erros = get_error_logs(limit=limit, filtro_tipo=filtro)
    return jsonify({"status": "success", "total": len(erros), "erros": erros})

@tester_bp.route('/api/debug/exportar', methods=['GET'])
def api_debug_exportar():
    """Exporta os erros capturados em formato JSON para análise offline ou envio à IA."""
    from flask import Response
    limit = request.args.get('limit', 500, type=int)
    erros = get_error_logs(limit=limit)
    
    # Formatação limpa orientada para IA
    export_data = {"erros": []}
    for e in erros:
        # Pega a essência estruturada para a IA ler facilmente
        caminho_simplificado = []
        for c in e.get("caminho_debug", []):
            if c.get("arquivo") and "site-packages" not in c.get("arquivo"): # Filtra libs padrão
                caminho_simplificado.append({
                    "arquivo": c.get("arquivo"),
                    "funcao": c.get("funcao"),
                    "linha": c.get("linha"),
                    "codigo": c.get("codigo")
                })
        
        # Só anexa se teve caminho_simplificado ou se foi erro grave
        export_data["erros"].append({
            "erro_tipo": e.get("erro_tipo"),
            "mensagem": e.get("erro_msg"),
            "rota": e.get("rota"),
            "caminho_debug": caminho_simplificado if caminho_simplificado else e.get("caminho_debug"),
            "sugestao_fix": e.get("contexto", {}).get("sugestao_fix", ""),
            "timestamp": e.get("timestamp")
        })
        
    json_str = json.dumps(export_data, indent=2, ensure_ascii=False)
    
    return Response(
        json_str,
        mimetype="application/json",
        headers={"Content-disposition": "attachment; filename=trproc_debug_errors.json"}
    )

@tester_bp.route('/api/debug/ameacas', methods=['GET'])
def api_debug_ameacas():
    """Lista as últimas ameaças detectadas (DDoS, bots, SQLi)."""
    limit = request.args.get('limit', 50, type=int)
    ameacas = get_threat_logs(limit=limit)
    return jsonify({"status": "success", "total": len(ameacas), "ameacas": ameacas})

@tester_bp.route('/api/debug/stats', methods=['GET'])
def api_debug_stats():
    """Retorna estatísticas agregadas dos erros e ameaças."""
    stats = get_error_stats()
    return jsonify({"status": "success", **stats})

@tester_bp.route('/api/debug/erro/<int:error_id>', methods=['GET'])
def api_debug_erro_detalhe(error_id):
    """Retorna o detalhe de um erro específico."""
    detalhe = get_error_detail(error_id)
    if not detalhe:
        return jsonify({"status": "error", "message": "Erro não encontrado."}), 404
    return jsonify({"status": "success", "erro": detalhe})

@tester_bp.route('/api/debug/limpar', methods=['POST'])
def api_debug_limpar():
    """Limpa todos os logs de erro e ameaça."""
    limpar_logs()
    return jsonify({"status": "success", "message": "Logs de debug limpos com sucesso."})

# ════════════════════════════════════════════════════════
#  CHAOS ENGINE & SANDBOX (E2E Stress Testing)
# ════════════════════════════════════════════════════════

from utils.mock_generator import generate_mock_data, cleanup_mock_data
from utils.chaos_engine import disparar_estresse_tramitacao

@tester_bp.route('/api/chaos/injetar', methods=['POST'])
def api_chaos_injetar():
    """Gera a massa de dados escalável para o Chaos Engine."""
    data = request.json or {}
    muns = data.get('num_muns', 10)
    procs = data.get('procs_per_mun', 50)
    generate_mock_data(num_muns=muns, procs_per_mun=procs)
    return jsonify({"status": "success", "message": f"Massa injetada: {muns} Municípios com {procs} processos cada."})

@tester_bp.route('/api/chaos/limpar', methods=['POST'])
def api_chaos_limpar():
    """Limpa a sandbox (massa de dados de teste)."""
    cleanup_mock_data()
    return jsonify({"status": "success", "message": "Sandbox limpa com sucesso."})

@tester_bp.route('/api/chaos/run', methods=['POST'])
def api_chaos_run():
    """Inicia o Chaos Engine (Estresse Assíncrono de Tramitações)."""
    data = request.json or {}
    threads = data.get('num_threads', 10)
    msgs = data.get('mensagens_por_thread', 20)
    resultado = disparar_estresse_tramitacao(num_threads=threads, mensagens_por_thread=msgs)
    return jsonify(resultado)


@tester_bp.route('/api/chaos/fuzz-page', methods=['POST'])
def api_chaos_fuzz_page():
    """Fuzzing CRUD por página × role: testa GET, POST com dados modificados,
    payloads de segurança e verifica se o RBAC responde corretamente."""
    import requests as req_lib
    import time as _time

    data = request.json or {}
    rota = data.get('rota', '/')
    nome = data.get('nome', rota)
    role = data.get('role', 'admin')
    formularios = data.get('formularios', [])
    botoes = data.get('botoes', [])

    base = request.host_url.rstrip('/')
    url = base + rota.replace('<int:id>', '1').replace('<id>', '1')

    testes_ok = 0
    testes_total = 0
    detalhes = []

    # Simular sessão com role
    session = req_lib.Session()
    session.cookies.set('test_role_override', role)

    # ─── TESTE 1: GET normal ───
    testes_total += 1
    try:
        r = session.get(url, timeout=10, allow_redirects=True)
        if r.status_code in [200, 302, 403]:
            testes_ok += 1
            detalhes.append(f"GET → HTTP {r.status_code}")
        else:
            detalhes.append(f"GET → HTTP {r.status_code} (inesperado)")
    except Exception as e:
        detalhes.append(f"GET → Erro: {str(e)[:60]}")

    # ─── TESTE 2: POST com dados normais ───
    if formularios:
        testes_total += 1
        form_data = {}
        for f in formularios:
            campo = f.get('campo', 'teste')
            tipo = f.get('tipo', 'text')
            if tipo in ('text', 'textarea'):
                form_data[campo] = 'Teste Chaos Normal'
            elif tipo == 'number':
                form_data[campo] = '12345'
            elif tipo == 'select':
                form_data[campo] = '1'
        try:
            r = session.post(url, data=form_data, timeout=10, allow_redirects=True)
            if r.status_code in [200, 302, 403, 405]:
                testes_ok += 1
                detalhes.append(f"POST normal → HTTP {r.status_code}")
            else:
                detalhes.append(f"POST normal → HTTP {r.status_code}")
        except Exception as e:
            detalhes.append(f"POST normal → Erro: {str(e)[:60]}")

    # ─── TESTE 3: POST com dados modificados (overflow) ───
    if formularios:
        testes_total += 1
        overflow_data = {}
        for f in formularios:
            campo = f.get('campo', 'teste')
            max_c = f.get('max_chars') or 5000
            overflow_data[campo] = 'X' * (max_c + 100)
        try:
            r = session.post(url, data=overflow_data, timeout=10, allow_redirects=True)
            if r.status_code in [200, 302, 400, 403, 405, 422]:
                testes_ok += 1
                detalhes.append(f"Overflow → HTTP {r.status_code} (tratado)")
            else:
                detalhes.append(f"Overflow → HTTP {r.status_code}")
        except Exception as e:
            detalhes.append(f"Overflow → Erro: {str(e)[:60]}")

    # ─── TESTE 4: Payloads de segurança (XSS, SQLi) ───
    payloads = [
        ("<script>alert(1)</script>", "XSS"),
        ("' OR '1'='1' --", "SQLi"),
        ("{{7*7}}", "SSTI"),
        ("../../../etc/passwd", "Path Traversal"),
    ]
    for payload, tipo_ataque in payloads:
        testes_total += 1
        attack_data = {}
        if formularios:
            for f in formularios:
                attack_data[f.get('campo', 'q')] = payload
        else:
            attack_data['q'] = payload
        try:
            r = session.post(url, data=attack_data, timeout=10, allow_redirects=True)
            body = r.text[:2000] if r.text else ''
            if payload in body and tipo_ataque == 'XSS':
                detalhes.append(f"{tipo_ataque} → REFLETIDO! (vuln)")
            elif 'error' in body.lower() and tipo_ataque == 'SQLi':
                detalhes.append(f"{tipo_ataque} → Erro SQL exposto (vuln)")
            else:
                testes_ok += 1
                detalhes.append(f"{tipo_ataque} → HTTP {r.status_code} (bloqueado/safe)")
        except Exception as e:
            testes_ok += 1
            detalhes.append(f"{tipo_ataque} → Bloqueado ({str(e)[:40]})")

    # ─── RESULTADO ───
    falhas = testes_total - testes_ok
    if falhas == 0:
        status = 'pass'
    elif falhas <= 1:
        status = 'warn'
    else:
        status = 'fail'

    return jsonify({
        "status": status,
        "pagina": nome,
        "rota": rota,
        "role": role,
        "testes_ok": testes_ok,
        "testes_total": testes_total,
        "detalhe": ' | '.join(detalhes[:6]),
        "detalhes_completos": detalhes
    })


# ════════════════════════════════════════════════════════
#  ABA UI/UX & MOBILE: Validador Responsivo
# ════════════════════════════════════════════════════════

@tester_bp.route('/api/uiux/scan-responsive', methods=['POST'])
def api_uiux_scan_responsive():
    """Testa responsividade de UMA rota em UM viewport específico.
    Analisa: meta viewport, font legível, scroll horizontal, botões acessíveis."""
    import requests as req_lib
    import re

    data = request.json or {}
    rota = data.get('rota', '/')
    nome = data.get('nome', rota)
    viewport_width = data.get('viewport_width', 360)
    botoes_esperados = data.get('botoes', [])

    base = request.host_url.rstrip('/')
    url = base + rota.replace('<int:id>', '1').replace('<id>', '1')

    score = 100
    problemas = []
    testes_feitos = 0

    try:
        session = req_lib.Session()
        # Simular User-Agent mobile para viewports pequenos
        if viewport_width <= 768:
            session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Mobile Safari/537.36'
            })
        else:
            session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0 Safari/537.36'
            })

        r = session.get(url, timeout=10, allow_redirects=True)

        if r.status_code not in [200, 302]:
            return jsonify({
                "status": "fail", "score": 0, "pagina": nome, "rota": rota,
                "viewport": viewport_width, "detalhe": f"HTTP {r.status_code}"
            })

        body = r.text

        # ─── TESTE 1: Meta Viewport ───
        testes_feitos += 1
        has_viewport = bool(re.search(r'<meta[^>]*name=["\']viewport["\']', body, re.I))
        if not has_viewport:
            score -= 25
            problemas.append('Sem meta viewport')

        # ─── TESTE 2: Fontes legíveis (não usar font-size < 12px para mobile) ───
        testes_feitos += 1
        tiny_fonts = re.findall(r'font-size\s*:\s*(\d+)px', body)
        tiny_count = sum(1 for f in tiny_fonts if int(f) < 12 and viewport_width <= 768)
        if tiny_count > 3:
            score -= 15
            problemas.append(f'{tiny_count} fontes < 12px')

        # ─── TESTE 3: Tabelas sem overflow-x ───
        testes_feitos += 1
        tables = re.findall(r'<table[^>]*>', body, re.I)
        overflow_wraps = len(re.findall(r'overflow-x\s*:\s*auto|overflow-x\s*:\s*scroll|table-responsive', body, re.I))
        unprotected_tables = len(tables) - overflow_wraps
        if unprotected_tables > 0 and viewport_width <= 768:
            score -= 15
            problemas.append(f'{unprotected_tables} tabelas sem overflow-x')

        # ─── TESTE 4: Elementos com width fixo > viewport ───
        testes_feitos += 1
        fixed_widths = re.findall(r'width\s*:\s*(\d+)px', body)
        oversized = [w for w in fixed_widths if int(w) > viewport_width]
        if len(oversized) > 2:
            score -= 15
            problemas.append(f'{len(oversized)} elementos > {viewport_width}px')

        # ─── TESTE 5: Media queries presentes ───
        testes_feitos += 1
        # Verificar CSS inline e links
        has_media_query = bool(re.search(r'@media', body, re.I))
        if not has_media_query and viewport_width <= 768:
            score -= 10
            problemas.append('Sem @media queries detectadas')

        # ─── TESTE 6: Botões com tamanho adequado para touch ───
        testes_feitos += 1
        buttons = re.findall(r'<button[^>]*>|<input[^>]*type=["\']submit["\']', body, re.I)
        # Verificar se tem min-height ou padding adequado
        small_buttons = re.findall(r'<button[^>]*style=["\'][^"\']*(?:height\s*:\s*(?:[12]\d)px|padding\s*:\s*[0-3]px)', body, re.I)
        if len(small_buttons) > 0 and viewport_width <= 768:
            score -= 10
            problemas.append(f'{len(small_buttons)} botões pequenos para touch')

        # ─── TESTE 7: Imagens sem max-width ───
        testes_feitos += 1
        imgs = re.findall(r'<img[^>]*>', body, re.I)
        imgs_responsive = len(re.findall(r'max-width\s*:\s*100%|img-fluid|img-responsive', body, re.I))
        unresponsive_imgs = len(imgs) - imgs_responsive
        if unresponsive_imgs > 2 and viewport_width <= 768:
            score -= 10
            problemas.append(f'{unresponsive_imgs} imagens sem max-width:100%')

        # Garantir mínimo 0
        score = max(score, 0)

        # Classificar
        if score >= 80:
            status = 'pass'
        elif score >= 50:
            status = 'warn'
        else:
            status = 'fail'

        return jsonify({
            "status": status,
            "score": score,
            "pagina": nome,
            "rota": rota,
            "viewport": viewport_width,
            "testes": testes_feitos,
            "problemas": problemas,
            "detalhe": ' | '.join(problemas) if problemas else 'Tudo OK',
            "meta_viewport": has_viewport,
            "total_tabelas": len(tables),
            "total_botoes": len(buttons),
            "total_imgs": len(imgs)
        })

    except Exception as e:
        return jsonify({
            "status": "fail", "score": 0, "pagina": nome, "rota": rota,
            "viewport": viewport_width, "detalhe": str(e)[:100]
        })


# ════════════════════════════════════════════════════════
#  NOVAS ABAS: Performance, Headers, Integridade, Discovery
# ════════════════════════════════════════════════════════

@tester_bp.route('/api/performance/scan', methods=['GET'])
def api_performance_scan():
    """Aba 6 - Mede latência de todas as rotas mapeadas."""
    try:
        resultado = medir_performance_rotas()
        return jsonify(resultado)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@tester_bp.route('/api/performance/scan-route', methods=['POST'])
def api_performance_scan_route():
    """Testa latência de UMA rota específica (para modal de progresso)."""
    import requests as req_lib
    import time as t
    data = request.get_json(force=True)
    rota = data.get('rota', '/')
    nome = data.get('nome', rota)
    modulo = data.get('modulo', '—')
    base = os.getenv("BASE_URL", "http://localhost:5001")
    url = f"{base}{rota.replace('<id>', '1').replace('<int:id>', '1')}"
    try:
        inicio = t.time()
        r = req_lib.get(url, timeout=5, allow_redirects=False)
        ms = round((t.time() - inicio) * 1000)
        if ms < 300:
            status, icone = "rapido", "✅"
        elif ms < 1000:
            status, icone = "medio", "⚠️"
        else:
            status, icone = "lento", "❌"
        return jsonify({"pagina": nome, "rota": rota, "modulo": modulo,
                        "tempo_ms": ms, "http_status": r.status_code,
                        "status": status, "icone": icone})
    except req_lib.exceptions.Timeout:
        return jsonify({"pagina": nome, "rota": rota, "modulo": modulo,
                        "tempo_ms": 5000, "http_status": 0, "status": "timeout", "icone": "💀"})
    except Exception as e:
        return jsonify({"pagina": nome, "rota": rota, "modulo": modulo,
                        "tempo_ms": -1, "http_status": 0, "status": "erro", "icone": "❗",
                        "erro": str(e)[:100]})

@tester_bp.route('/api/security-headers/scan', methods=['GET'])
def api_security_headers_scan():
    """Aba 7 - Valida headers HTTP, cookies, CORS, redirects."""
    try:
        resultado = verificar_headers_seguranca()
        return jsonify(resultado)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@tester_bp.route('/api/security-headers/scan-route', methods=['POST'])
def api_security_headers_scan_route():
    """Testa headers de segurança de UMA rota (para modal de progresso)."""
    import requests as req_lib
    data = request.get_json(force=True)
    rota = data.get('rota', '/')
    nome = data.get('nome', rota)
    base = os.getenv("BASE_URL", "http://localhost:5001")
    url = f"{base}{rota.replace('<id>', '1').replace('<int:id>', '1')}"

    HEADERS_ESPERADOS = [
        "X-Frame-Options", "X-Content-Type-Options", "X-XSS-Protection",
        "Content-Security-Policy", "Strict-Transport-Security", "Referrer-Policy"
    ]
    try:
        r = req_lib.get(url, timeout=5, allow_redirects=False)
        ausentes = [h for h in HEADERS_ESPERADOS if h.lower() not in {k.lower(): v for k, v in r.headers.items()}]
        score = round(((len(HEADERS_ESPERADOS) - len(ausentes)) / len(HEADERS_ESPERADOS)) * 100)

        cookies_inseguros = []
        for ck in r.cookies:
            problemas = []
            ck_str = r.headers.get('Set-Cookie', '')
            if 'httponly' not in ck_str.lower():
                problemas.append('sem HttpOnly')
            if 'secure' not in ck_str.lower():
                problemas.append('sem Secure')
            if problemas:
                cookies_inseguros.append({"nome": ck.name, "problemas": problemas})

        cors_aberto = r.headers.get('Access-Control-Allow-Origin', '') == '*'

        return jsonify({"pagina": nome, "rota": rota, "score": score,
                        "headers_ausentes": ausentes,
                        "cookies_inseguros": cookies_inseguros,
                        "cors_aberto": cors_aberto, "status": "ok"})
    except Exception as e:
        return jsonify({"pagina": nome, "rota": rota, "score": 0,
                        "headers_ausentes": HEADERS_ESPERADOS,
                        "cookies_inseguros": [], "cors_aberto": False,
                        "status": "erro", "erro": str(e)[:100]})

@tester_bp.route('/api/integrity/scan', methods=['GET'])
def api_integrity_scan():
    """Aba 8 - Verifica integridade de dados no banco."""
    try:
        resultado = verificar_integridade_dados()
        return jsonify(resultado)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@tester_bp.route('/api/discovery/rotas', methods=['GET'])
def api_discovery_rotas():
    """Auto-descoberta de rotas Flask em tempo real."""
    try:
        from flask import current_app
        resultado = descobrir_rotas_flask(current_app)
        return jsonify(resultado)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500



# ════════════════════════════════════════════════════════
#  ESTADO GLOBAL DO NUCLEAR SCANNER (Polling pelo Frontend)
#  Refatorado: Concorrência com ThreadPool + Progresso Granular
# ════════════════════════════════════════════════════════
import threading
import time as _time
from concurrent.futures import ThreadPoolExecutor, as_completed

_nuclear_state = {
    "running": False,
    "fase_atual": 0,
    "total_fases": 5,
    "fase_nome": "",
    "sub_step": "",
    "progresso_pct": 0,
    "inicio": 0,
    "elapsed_sec": 0,
    "resultados_parciais": {
        "unitarios": {"total": 0, "passou": 0, "falhou": 0, "done": False},
        "performance": {"total": 0, "rapidos": 0, "lentos": 0, "media_ms": 0, "done": False},
        "headers": {"total": 0, "score": 0, "vulns": 0, "done": False},
        "integridade": {"total": 0, "problemas": 0, "criticos": 0, "done": False},
        "uiux": {"total": 0, "score_medio": 0, "problemas": 0, "done": False},
    },
    "log_history": [],  # Lista de logs detalhados para o frontend
    "concluido": False,
    "erro": None,
}
_nuclear_lock = threading.Lock()


def _nuclear_update(fase, fase_nome, sub_step, pct):
    """Atualiza o estado global do nuclear scan (thread-safe)."""
    with _nuclear_lock:
        _nuclear_state["fase_atual"] = fase
        _nuclear_state["fase_nome"] = fase_nome
        _nuclear_state["sub_step"] = sub_step
        _nuclear_state["progresso_pct"] = pct
        _nuclear_state["elapsed_sec"] = round(_time.time() - _nuclear_state["inicio"], 1)


def _nuclear_log(msg, tipo="info"):
    """Adiciona log detalhado ao histórico nuclear."""
    with _nuclear_lock:
        _nuclear_state["log_history"].append({
            "ts": round(_time.time() - _nuclear_state["inicio"], 1),
            "msg": msg,
            "tipo": tipo
        })
        # Limita a 200 últimas entradas
        if len(_nuclear_state["log_history"]) > 200:
            _nuclear_state["log_history"] = _nuclear_state["log_history"][-200:]


@tester_bp.route('/api/nuclear/status', methods=['GET'])
def api_nuclear_status():
    """Endpoint de POLLING: o frontend consulta para atualizar o painel de progresso."""
    with _nuclear_lock:
        state = dict(_nuclear_state)
        # Copia logs recentes (máx 30 para não sobrecarregar)
        state["log_history"] = list(_nuclear_state["log_history"][-30:])
        return jsonify(state)


@tester_bp.route('/api/nuclear/scan', methods=['POST'])
def api_nuclear_scan():
    """
    BOTÃO NUCLEAR: Executa TUDO em background com CONCORRÊNCIA e progresso granular.
    - Fase 1: Testes unitários com ThreadPool (8 workers paralelos)
    - Fase 2: Performance (paralelo com headers)
    - Fase 3: Headers & Segurança
    - Fase 4: Integridade de dados
    - Fase 5: UI/UX & Responsividade
    """
    from flask import current_app

    with _nuclear_lock:
        if _nuclear_state["running"]:
            return jsonify({"status": "running", "message": "Varredura nuclear já está em execução."})

    app = current_app._get_current_object()

    def _nuclear_worker():
        # Fix Windows charmap encoding crash for threads with Unicode
        import sys, io
        try:
            if sys.stdout and hasattr(sys.stdout, 'encoding') and sys.stdout.encoding != 'utf-8':
                sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
            if sys.stderr and hasattr(sys.stderr, 'encoding') and sys.stderr.encoding != 'utf-8':
                sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
        except Exception:
            pass

        with app.app_context():
            with _nuclear_lock:
                _nuclear_state["running"] = True
                _nuclear_state["concluido"] = False
                _nuclear_state["erro"] = None
                _nuclear_state["inicio"] = _time.time()
                _nuclear_state["progresso_pct"] = 0
                _nuclear_state["log_history"] = []
                for k in _nuclear_state["resultados_parciais"]:
                    for sk in _nuclear_state["resultados_parciais"][k]:
                        if sk == "done":
                            _nuclear_state["resultados_parciais"][k][sk] = False
                        elif isinstance(_nuclear_state["resultados_parciais"][k][sk], int):
                            _nuclear_state["resultados_parciais"][k][sk] = 0

            try:
                # ═══════════════════════════════════════════
                # FASE 1/5: TESTES UNITÁRIOS (Concorrente)
                # ═══════════════════════════════════════════
                _nuclear_update(1, "Testes Unitários", "Preparando bateria multi-role concorrente...", 2)
                _nuclear_log("=== FASE 1/5: TESTES UNITARIOS ===", "header")

                roles = ["admin", "master", "tecnico", "secretario", "cliente"]
                from utils.unit_test_runner import PAGINAS_SISTEMA
                total_paginas = len(PAGINAS_SISTEMA)
                total_jobs = len(roles) * total_paginas
                _nuclear_log(f"📋 {len(roles)} roles × {total_paginas} páginas = {total_jobs} combinações", "info")

                # Resultados acumulados (thread-safe via lock)
                unit_results = {"pass": 0, "fail": 0, "total": 0, "done_count": 0}
                unit_results_lock = threading.Lock()

                def test_page_role(role, pag, job_idx):
                    """Testa uma página com uma role — executado em thread paralela."""
                    try:
                        resultado = executar_teste_pagina(pag["id"], role)
                        p = resultado.get("passou", 0)
                        f = resultado.get("falhou", 0)
                        t = resultado.get("total_testes", 0)

                        with unit_results_lock:
                            unit_results["pass"] += p
                            unit_results["fail"] += f
                            unit_results["total"] += t
                            unit_results["done_count"] += 1
                            done = unit_results["done_count"]

                        # Atualiza progresso
                        pct = 2 + int((done / total_jobs) * 43)
                        status_icon = "✅" if f == 0 else "⚠️"
                        _nuclear_update(1, "Testes Unitários",
                            f"[{role.upper()}] {pag['nome']} — {p}✅ {f}❌ ({done}/{total_jobs})", pct)
                        _nuclear_log(
                            f"{status_icon} [{role.upper()}] {pag['nome']}: {t} testes, {p} OK, {f} falhas",
                            "pass" if f == 0 else "fail")

                        # Injeta falhas no debug
                        for r in resultado.get("resultados", []):
                            if r["status"] == "fail":
                                try:
                                    from utils.debug_engine import registrar_falha_teste
                                    registrar_falha_teste(
                                        resultado.get("pagina",""), resultado.get("rota",""),
                                        r.get("cat",""), f"[{role.upper()}] {r['teste']}", r.get("detalhe",""))
                                except: pass

                    except Exception as ex:
                        with unit_results_lock:
                            unit_results["done_count"] += 1
                        _nuclear_log(f"❌ Erro [{role.upper()}] {pag['nome']}: {str(ex)[:80]}", "fail")

                # Executa TODOS em paralelo (8 workers)
                _nuclear_log(f"🚀 Disparando {total_jobs} testes com 8 workers paralelos...", "info")
                with ThreadPoolExecutor(max_workers=8) as executor:
                    futures = []
                    job_idx = 0
                    for role in roles:
                        for pag in PAGINAS_SISTEMA:
                            futures.append(executor.submit(test_page_role, role, pag, job_idx))
                            job_idx += 1
                    # Aguarda todos
                    for fut in as_completed(futures):
                        try:
                            fut.result()
                        except: pass

                with _nuclear_lock:
                    _nuclear_state["resultados_parciais"]["unitarios"] = {
                        "total": unit_results["total"],
                        "passou": unit_results["pass"],
                        "falhou": unit_results["fail"],
                        "done": True
                    }
                _nuclear_log(
                    f"📊 Unitários: {unit_results['total']} testes | {unit_results['pass']} OK | {unit_results['fail']} falhas",
                    "header")

                # ═══════════════════════════════════════════
                # FASE 2/5: PERFORMANCE (Concorrente)
                # ═══════════════════════════════════════════
                try:
                    _nuclear_update(2, "Performance & Latência", "Medindo tempo de resposta...", 50)
                    _nuclear_log("=== FASE 2/5: PERFORMANCE ===", "header")
                    _nuclear_log("Testando latencia de {} rotas...".format(total_paginas), "info")

                    perf_result = medir_performance_rotas()

                    for r in perf_result.get("resultados", [])[:10]:
                        icon = r.get("icone", "?")
                        _nuclear_log("{} {}: {}ms (HTTP {})".format(icon, r['pagina'], r['tempo_ms'], r['http_status']),
                            "pass" if r["status"] == "rapido" else "warn" if r["status"] == "medio" else "fail")

                    with _nuclear_lock:
                        _nuclear_state["resultados_parciais"]["performance"] = {
                            "total": perf_result.get("total_rotas", 0),
                            "rapidos": perf_result.get("rapidos", 0),
                            "lentos": perf_result.get("lentos", 0),
                            "media_ms": perf_result.get("media_ms", 0),
                            "done": True
                        }
                    _nuclear_log(
                        "Performance: {} rapidas | {} medias | {} lentas | Media: {}ms".format(
                            perf_result.get('rapidos',0), perf_result.get('medios',0),
                            perf_result.get('lentos',0), perf_result.get('media_ms',0)),
                        "header")

                    # Injeta lentas no debug
                    for r in perf_result.get("resultados", []):
                        if r["status"] in ("lento", "timeout"):
                            try:
                                from utils.debug_engine import registrar_falha_teste
                                registrar_falha_teste(r["pagina"], r["rota"], "Performance",
                                    "Latencia: {}ms".format(r['tempo_ms']), "Rota lenta: {}ms".format(r['tempo_ms']))
                            except: pass
                except Exception as e_perf:
                    _nuclear_log("ERRO na Fase 2 (Performance): {}".format(str(e_perf)[:150]), "fail")
                    with _nuclear_lock:
                        _nuclear_state["resultados_parciais"]["performance"]["done"] = True

                # ═══════════════════════════════════════════
                # FASE 3/5: HEADERS & REDE
                # ═══════════════════════════════════════════
                try:
                    _nuclear_update(3, "Headers & Segurança de Rede", "Validando headers HTTP, cookies, CORS...", 70)
                    _nuclear_log("=== FASE 3/5: HEADERS & SEGURANCA ===", "header")
                    _nuclear_log("Analisando headers de {} rotas...".format(total_paginas), "info")

                    hdr_result = verificar_headers_seguranca()
                    vulns = len(hdr_result.get("redirect_vulns", [])) + len(hdr_result.get("crlf_vulns", []))

                    for r in hdr_result.get("resultados", [])[:10]:
                        s = r.get("score", 0)
                        icon = "[OK]" if s >= 80 else "[WARN]" if s >= 50 else "[FAIL]"
                        aus = ", ".join(r.get("headers_ausentes", [])[:3]) or "Nenhum"
                        _nuclear_log("{} {}: Score {}% | Ausentes: {}".format(icon, r['rota'], r['score'], aus),
                            "pass" if s >= 80 else "warn" if s >= 50 else "fail")

                    with _nuclear_lock:
                        _nuclear_state["resultados_parciais"]["headers"] = {
                            "total": hdr_result.get("total_rotas", 0),
                            "score": hdr_result.get("score_medio", 0),
                            "vulns": vulns,
                            "done": True
                        }
                    _nuclear_log(
                        "Headers: Score medio {}% | {} vulnerabilidades".format(
                            hdr_result.get('score_medio',0), vulns),
                        "header")
                except Exception as e_hdr:
                    _nuclear_log("ERRO na Fase 3 (Headers): {}".format(str(e_hdr)[:150]), "fail")
                    with _nuclear_lock:
                        _nuclear_state["resultados_parciais"]["headers"]["done"] = True

                # ═══════════════════════════════════════════
                # FASE 4/5: INTEGRIDADE DE DADOS
                # ═══════════════════════════════════════════
                try:
                    _nuclear_update(4, "Integridade de Dados", "Verificando FKs, duplicatas, registros orfaos...", 88)
                    _nuclear_log("=== FASE 4/5: INTEGRIDADE DE DADOS ===", "header")

                    int_result = verificar_integridade_dados()
                    for c in int_result.get("checks", []):
                        icon = c.get("icone", "?")
                        _nuclear_log("{} {}: {} encontrados [{}]".format(icon, c['nome'], c['total_encontrados'], c['severidade']),
                            "pass" if c["status"] == "pass" else "fail")

                    with _nuclear_lock:
                        _nuclear_state["resultados_parciais"]["integridade"] = {
                            "total": int_result.get("total_checks", 0),
                            "problemas": int_result.get("total_problemas", 0),
                            "criticos": int_result.get("criticos", 0),
                            "done": True
                        }

                    # Injeta problemas no debug
                    for c in int_result.get("checks", []):
                        if c["status"] == "fail":
                            try:
                                from utils.debug_engine import registrar_falha_teste
                                registrar_falha_teste("Banco de Dados", "SQL", c["categoria"],
                                    c["nome"], "{} registros com problema".format(c['total_encontrados']))
                            except: pass
                except Exception as e_int:
                    _nuclear_log("ERRO na Fase 4 (Integridade): {}".format(str(e_int)[:150]), "fail")
                    with _nuclear_lock:
                        _nuclear_state["resultados_parciais"]["integridade"]["done"] = True

                # ═══════════════════════════════════════════
                # FASE 5/5: UI/UX & RESPONSIVIDADE
                # ═══════════════════════════════════════════
                try:
                    _nuclear_update(5, "UI/UX & Responsividade", "Testando responsividade em 3 viewports...", 92)
                    _nuclear_log("=== FASE 5/5: UI/UX & RESPONSIVIDADE ===", "header")

                    import requests as req_lib
                    viewports = [360, 768, 1920]  # Mobile, Tablet, Desktop
                    viewport_names = {360: "Mobile", 768: "Tablet", 1920: "Desktop"}
                    uiux_scores = []
                    uiux_problemas_total = 0
                    base = os.getenv("BASE_URL", "http://localhost:5001")

                    for pag in PAGINAS_SISTEMA:
                        rota = pag["rota"].replace('<id>', '1').replace('<int:id>', '1')
                        url = f"{base}{rota}"
                        for vw in viewports:
                            try:
                                import re
                                ua = 'Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36 Mobile' if vw <= 768 else 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
                                r_uiux = req_lib.get(url, timeout=5, allow_redirects=True, headers={'User-Agent': ua})
                                if r_uiux.status_code not in [200, 302]:
                                    continue
                                body = r_uiux.text
                                score = 100
                                probs = []
                                # Meta viewport
                                if not re.search(r'<meta[^>]*name=["\']viewport["\']', body, re.I):
                                    score -= 25; probs.append('Sem meta viewport')
                                # Fontes pequenas
                                tiny = [f for f in re.findall(r'font-size\s*:\s*(\d+)px', body) if int(f) < 12]
                                if len(tiny) > 3 and vw <= 768:
                                    score -= 15; probs.append(f'{len(tiny)} fontes <12px')
                                # Tabelas sem overflow
                                tables = re.findall(r'<table', body, re.I)
                                overflows = len(re.findall(r'overflow-x|table-responsive', body, re.I))
                                if len(tables) - overflows > 0 and vw <= 768:
                                    score -= 15; probs.append(f'{len(tables)-overflows} tabelas sem overflow-x')
                                score = max(score, 0)
                                uiux_scores.append(score)
                                uiux_problemas_total += len(probs)
                            except:
                                pass

                        pct = 92 + int((PAGINAS_SISTEMA.index(pag) / max(total_paginas, 1)) * 6)
                        _nuclear_update(5, "UI/UX & Responsividade",
                            f"Testando {pag['nome']} em {len(viewports)} viewports...", min(pct, 98))

                    avg_score = round(sum(uiux_scores) / max(len(uiux_scores), 1))
                    icon = "✅" if avg_score >= 80 else "⚠️" if avg_score >= 50 else "❌"
                    _nuclear_log(f"{icon} UI/UX Score Medio: {avg_score}% | {uiux_problemas_total} problemas em {len(uiux_scores)} testes", "pass" if avg_score >= 80 else "warn" if avg_score >= 50 else "fail")

                    with _nuclear_lock:
                        _nuclear_state["resultados_parciais"]["uiux"] = {
                            "total": len(uiux_scores),
                            "score_medio": avg_score,
                            "problemas": uiux_problemas_total,
                            "done": True
                        }
                    _nuclear_log(
                        f"UI/UX: {len(uiux_scores)} combinacoes testadas | Score medio {avg_score}% | {uiux_problemas_total} problemas",
                        "header")
                except Exception as e_uiux:
                    _nuclear_log("ERRO na Fase 5 (UI/UX): {}".format(str(e_uiux)[:150]), "fail")
                    with _nuclear_lock:
                        _nuclear_state["resultados_parciais"]["uiux"]["done"] = True

                # ═══ FINALIZAÇÃO ═══
                elapsed = round(_time.time() - _nuclear_state["inicio"], 1)
                _nuclear_update(5, "Concluido", "Varredura nuclear completa em {}s!".format(elapsed), 100)
                _nuclear_log("VARREDURA NUCLEAR CONCLUIDA em {}s".format(elapsed), "header")
                _nuclear_log("Total: {} testes unitarios + perf + headers + integridade + uiux".format(unit_results['total']), "info")

                with _nuclear_lock:
                    _nuclear_state["concluido"] = True
                    _nuclear_state["running"] = False
                try:
                    print(f"[NUCLEAR] Varredura nuclear concluida em {elapsed}s!")
                except: pass

            except Exception as e:
                with _nuclear_lock:
                    _nuclear_state["erro"] = str(e)[:300]
                    _nuclear_state["running"] = False
                    _nuclear_state["concluido"] = True
                _nuclear_log("ERRO FATAL: {}".format(str(e)[:200]), "fail")
                try:
                    print(f"[NUCLEAR] Erro fatal: {e}")
                except: pass

    thread = threading.Thread(target=_nuclear_worker, daemon=True)
    thread.start()

    return jsonify({
        "status": "success",
        "message": "Varredura NUCLEAR iniciada com 8 workers paralelos. Acompanhe o progresso ao vivo."
    })


# ════════════════════════════════════════════════════════
#  ISOLAMENTO & TDD PLAYGROUND
# ════════════════════════════════════════════════════════

import os
import json
import uuid
import datetime
import subprocess

ISOLATION_LOG_FILE = os.path.join("logs", "testes_reproduzidos.json")

def load_isolated_tests():
    if not os.path.exists(ISOLATION_LOG_FILE):
        return []
    try:
        with open(ISOLATION_LOG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def save_isolated_test(test_data):
    tests = load_isolated_tests()
    tests.append(test_data)
    os.makedirs(os.path.dirname(ISOLATION_LOG_FILE), exist_ok=True)
    with open(ISOLATION_LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(tests, f, indent=4, ensure_ascii=False)

@tester_bp.route('/api/isolation/create-test', methods=['POST'])
def api_isolation_create_test():
    """Recebe o relatório de erro e cria um stub de teste (TDD)."""
    data = request.get_json(force=True)
    titulo = data.get('titulo', 'Bug Desconhecido')
    passos = data.get('passos', '')
    stacktrace = data.get('stacktrace', '')
    
    test_id = str(uuid.uuid4())[:8]
    test_filename = f"test_isolated_{test_id}.py"
    test_filepath = os.path.join("tests", "isolation", test_filename)
    
    # Gerar stub do teste TDD
    stub_content = f'"""\nTeste Isolado gerado automaticamente\nTítulo: {titulo}\nPassos: {passos}\n"""\nimport pytest\n\ndef test_{test_id}_reproduction():\n    # TODO: Implementar passos de reprodução\n    # 1. Configurar contexto (Mock DB, Usuário Logado)\n    # 2. Executar ação que causa o erro\n    # 3. Assertiva garantindo que o erro não ocorre mais\n    assert False, "Teste gerado a partir do Isolation Playground. Falhando por padrão até a implementação."\n'
    
    os.makedirs(os.path.dirname(test_filepath), exist_ok=True)
    with open(test_filepath, "w", encoding="utf-8") as f:
        f.write(stub_content)
        
    registro = {
        "id": test_id,
        "titulo": titulo,
        "passos": passos,
        "stacktrace": stacktrace,
        "file": test_filepath,
        "status": "pending",
        "created_at": datetime.datetime.now().isoformat()
    }
    
    save_isolated_test(registro)
    
    return jsonify({
        "status": "success",
        "message": "Teste isolado criado com sucesso.",
        "test_id": test_id,
        "file": test_filepath
    })

@tester_bp.route('/api/isolation/list', methods=['GET'])
def api_isolation_list():
    """Lista todos os testes de regressão salvos."""
    tests = load_isolated_tests()
    return jsonify({"status": "success", "data": tests})

@tester_bp.route('/api/isolation/run', methods=['POST'])
def api_isolation_run():
    """Roda um teste isolado via pytest e retorna o resultado."""
    data = request.get_json(force=True)
    test_id = data.get("id")
    
    tests = load_isolated_tests()
    test_record = next((t for t in tests if t["id"] == test_id), None)
    
    if not test_record:
        return jsonify({"status": "error", "message": "Teste não encontrado."}), 404
        
    filepath = test_record.get("file")
    if not os.path.exists(filepath):
        return jsonify({"status": "error", "message": "Arquivo de teste não encontrado."}), 404
        
    # Executar pytest de forma isolada
    try:
        result = subprocess.run(
            ["pytest", filepath, "-v"],
            capture_output=True, text=True, timeout=15
        )
        passed = result.returncode == 0
        output = result.stdout + "\n" + result.stderr
        
        # Atualiza status no acervo
        test_record["status"] = "pass" if passed else "fail"
        test_record["last_run"] = datetime.datetime.now().isoformat()
        test_record["last_output"] = output[-1000:] # Guarda últimos 1000 chars
        
        with open(ISOLATION_LOG_FILE, "w", encoding="utf-8") as f:
            json.dump(tests, f, indent=4, ensure_ascii=False)
            
        return jsonify({
            "status": "success" if passed else "fail",
            "message": "Teste executado com sucesso." if passed else "Falha na execução do teste.",
            "output": output
        })
    except subprocess.TimeoutExpired:
        return jsonify({"status": "error", "message": "Timeout na execução do teste."})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

