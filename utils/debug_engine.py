"""
TRPROC — Motor de Debug & Análise de Erros
============================================
Captura, cataloga e analisa todos os erros do sistema em tempo real.
Funciona como um console.log / error_log inteligente que:
  1. Captura erros automaticamente via Flask error handler
  2. Rastreia o caminho completo do erro (rota → função → linha)
  3. Compila contexto global para ajudar a consertar cada erro
  4. Detecta padrões de ataque (DDoS, brute force, bot flood)
  5. Persiste logs em memória para a sessão de dev (sem DB)
"""
import os
import json
import ast
import time
import traceback
import threading
from datetime import datetime
from collections import deque, defaultdict

# ════════════════════════════════════════════════════════
#  ARMAZENAMENTO EM MEMÓRIA (volátil — reseta ao reiniciar)
# ════════════════════════════════════════════════════════

# Logs de erros (últimos 500)
_error_log = deque(maxlen=500)

# Logs de requisições suspeitas (últimos 200)
_threat_log = deque(maxlen=200)

# Contador de requisições por IP (para detecção de DDoS)
_request_counter = defaultdict(list)  # IP -> [timestamps]

# Lock para thread safety
_lock = threading.Lock()

# Configurações de detecção de ameaças
RATE_LIMIT_WINDOW = 60    # Janela em segundos
RATE_LIMIT_MAX = 100      # Max requests por IP na janela
BOT_SIGNATURES = [
    'sqlmap', 'nikto', 'nmap', 'dirbuster', 'gobuster', 'wfuzz',
    'burpsuite', 'hydra', 'medusa', 'masscan', 'zap', 'nuclei',
    'python-requests', 'curl/', 'wget/', 'scrapy'
]
SUSPICIOUS_PATHS = [
    '/wp-admin', '/wp-login', '/.env', '/phpinfo', '/phpmyadmin',
    '/admin/config.php', '/.git', '/actuator', '/solr', '/api/v1/../',
    '/shell', '/cmd', '/eval', '/exec'
]

# Configuração de Persistência
LOGS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.logs')
if not os.path.exists(LOGS_DIR):
    os.makedirs(LOGS_DIR, exist_ok=True)
LOGS_FILE = os.path.join(LOGS_DIR, 'debug_logs.json')

def _salvar_logs():
    try:
        # A cópia precisa ser rápida para não travar a thread.
        erros_dump = list(_error_log)
        ameacas_dump = list(_threat_log)
        # Salva num arquivo paralelo e renomeia (atomic)
        temp_file = LOGS_FILE + '.tmp'
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump({"erros": erros_dump, "ameacas": ameacas_dump}, f, ensure_ascii=False)
        os.replace(temp_file, LOGS_FILE)
    except Exception as e:
        pass

def _carregar_logs():
    try:
        if os.path.exists(LOGS_FILE):
            with open(LOGS_FILE, 'r', encoding='utf-8') as f:
                dados = json.load(f)
                # Inverte a ordem para manter a lógica deque.appendleft
                for e in reversed(dados.get('erros', [])):
                    _error_log.appendleft(e)
                for a in reversed(dados.get('ameacas', [])):
                    _threat_log.appendleft(a)
    except:
        pass

_carregar_logs()


def capturar_erro(request_obj, exception, response_code=500):
    """
    Captura um erro do Flask e cria um registro completo de debug.
    Chamado automaticamente pelo error handler do Flask.
    """
    agora = datetime.now()
    tb = traceback.format_exception(type(exception), exception, exception.__traceback__)
    
    # Monta o "caminho de debug" — da requisição até o erro
    caminho_debug = []
    for frame in traceback.extract_tb(exception.__traceback__):
        caminho_debug.append({
            "arquivo": frame.filename.replace('\\', '/').split('trproc-main-trproc/')[-1],
            "funcao": frame.name,
            "linha": frame.lineno,
            "codigo": frame.line or ""
        })
    
    registro = {
        "id": int(agora.timestamp() * 1000),
        "timestamp": agora.strftime("%d/%m/%Y %H:%M:%S"),
        "timestamp_raw": agora.timestamp(),
        "tipo": "erro",
        "status_code": response_code,
        "metodo": request_obj.method if request_obj else "?",
        "rota": request_obj.path if request_obj else "?",
        "url_completa": request_obj.url if request_obj else "?",
        "ip": request_obj.remote_addr if request_obj else "?",
        "user_agent": request_obj.headers.get('User-Agent', '?')[:200] if request_obj else "?",
        "erro_tipo": type(exception).__name__,
        "erro_msg": str(exception)[:500],
        "caminho_debug": caminho_debug,
        "traceback_completo": ''.join(tb)[-3000:],  # Últimos 3000 chars do traceback
        "query_params": dict(request_obj.args) if request_obj else {},
        "form_data_keys": list(request_obj.form.keys()) if request_obj and request_obj.form else [],
        "contexto": _compilar_contexto(request_obj, exception, caminho_debug)
    }
    
    with _lock:
        _error_log.appendleft(registro)
    
    # Executa salvamento em background
    threading.Thread(target=_salvar_logs).start()
    
    return registro


def _compilar_contexto(request_obj, exception, caminho):
    """
    Compila o contexto inteligente que ajuda a entender e corrigir o erro.
    Funciona como um 'compilador de conhecimento' sobre o que aconteceu.
    """
    contexto = {
        "resumo": "",
        "possivel_causa": "",
        "sugestao_fix": "",
        "pilar_relacionado": ""
    }
    
    erro_tipo = type(exception).__name__
    erro_msg = str(exception).lower()
    rota = request_obj.path if request_obj else ""
    
    # ── Análise por tipo de erro ──
    if 'OperationalError' in erro_tipo or 'mysql' in erro_msg:
        contexto["resumo"] = "Erro de banco de dados MySQL"
        contexto["possivel_causa"] = "Query SQL malformada, conexão perdida, ou tabela inexistente"
        contexto["sugestao_fix"] = "Verificar se a tabela existe no banco. Usar Monster (/admin/monster) para testar a query manualmente."
        contexto["pilar_relacionado"] = "Pilar 2 (Multi-Tenant) — Verificar se o município_id está na query"
        
    elif 'TemplateNotFound' in erro_tipo or 'jinja' in erro_msg:
        contexto["resumo"] = "Template HTML não encontrado"
        contexto["possivel_causa"] = f"Arquivo .html faltando na pasta templates/"
        contexto["sugestao_fix"] = "Verificar se o template referenciado na rota existe e o nome está correto."
        contexto["pilar_relacionado"] = "Pilar 10 (UX Premium)"
        
    elif 'KeyError' in erro_tipo:
        contexto["resumo"] = "Chave não encontrada em dicionário/sessão"
        contexto["possivel_causa"] = f"Tentou acessar '{exception}' que não existe no objeto"
        contexto["sugestao_fix"] = "Usar .get('chave', valor_default) em vez de ['chave'] direto."
        contexto["pilar_relacionado"] = "Pilar 0 (Anti-Regressão)"
        
    elif 'TypeError' in erro_tipo:
        contexto["resumo"] = "Tipo de dado incompatível"
        contexto["possivel_causa"] = "Variável None sendo usada como string/int, ou argumento faltando"
        contexto["sugestao_fix"] = "Adicionar checagem de tipo antes da operação. Usar input-sanitizer-translator."
        contexto["pilar_relacionado"] = "Pilar 5 (Formulários Dinâmicos)"
        
    elif 'ValueError' in erro_tipo:
        contexto["resumo"] = "Valor inválido recebido"
        contexto["possivel_causa"] = "Conversão de tipo falhou (ex: int('abc'))"
        contexto["sugestao_fix"] = "Validar input antes de converter. Aplicar sanitizar_input()."
        contexto["pilar_relacionado"] = "Pilar 0 (Anti-Regressão)"
        
    elif 'AttributeError' in erro_tipo:
        contexto["resumo"] = "Atributo não encontrado no objeto"
        contexto["possivel_causa"] = "Objeto é None ou do tipo errado"
        contexto["sugestao_fix"] = "Verificar se o objeto foi inicializado corretamente antes de acessar o atributo."
        contexto["pilar_relacionado"] = "Pilar 0 (Anti-Regressão)"
        
    elif 'PermissionError' in erro_tipo or 'Forbidden' in erro_msg:
        contexto["resumo"] = "Acesso negado / permissão insuficiente"
        contexto["possivel_causa"] = "Usuário tentou acessar recurso sem nível adequado"
        contexto["sugestao_fix"] = "Verificar a matriz RBAC em /admin/rbac."
        contexto["pilar_relacionado"] = "Pilar 3 (Autenticação e RBAC)"
        
    elif '404' in erro_msg or 'NotFound' in erro_tipo:
        contexto["resumo"] = "Recurso ou Rota não encontrada"
        contexto["possivel_causa"] = "Pode ser um link quebrado (erro de arquivo/caminho) ou bot procurando vulnerabilidade."
        contexto["sugestao_fix"] = "Se for usuário comum: corrigir href/src. Se for bot (ver IP/User-Agent): ignorar/bloquear."
        contexto["pilar_relacionado"] = "Nenhum (Erro de Path/Link)"
    else:
        contexto["resumo"] = f"Erro de Lógica/Código: {erro_tipo}"
        contexto["possivel_causa"] = erro_msg[:200]
        contexto["sugestao_fix"] = "Analisar o traceback completo e o caminho de debug para identificar a causa raiz."
        contexto["pilar_relacionado"] = "Pilar 0 (Anti-Regressão)"
    
    # ── Enriquecimento por rota ──
    if '/admin/' in rota:
        contexto["pilar_relacionado"] += " | Pilar 3 (RBAC)"
    if '/processo/' in rota or '/processos' in rota:
        contexto["pilar_relacionado"] += " | Pilar 1 (Tramitação)"
    if '/cadastro' in rota:
        contexto["pilar_relacionado"] += " | Pilar 6 (Cadastros Dinâmicos)"
    
    return contexto


def analisar_requisicao(request_obj):
    """
    Analisa cada requisição em busca de padrões de ataque.
    Chamado pelo before_request do Flask.
    Retorna dict de ameaça se detectar, None se OK.
    """
    ip = request_obj.remote_addr or "?"
    user_agent = (request_obj.headers.get('User-Agent', '') or '').lower()
    path = request_obj.path.lower()
    agora = time.time()
    
    ameaca = None
    
    # ── 1. Rate Limiting (DDoS / Brute Force) ──
    with _lock:
        _request_counter[ip].append(agora)
        # Limpar timestamps antigos
        _request_counter[ip] = [t for t in _request_counter[ip] if agora - t < RATE_LIMIT_WINDOW]
        
        if len(_request_counter[ip]) > RATE_LIMIT_MAX:
            ameaca = {
                "tipo": "RATE_LIMIT",
                "severidade": "ALTA",
                "descricao": f"IP {ip} excedeu {RATE_LIMIT_MAX} requisições em {RATE_LIMIT_WINDOW}s ({len(_request_counter[ip])} reqs)",
                "acao": "Considerar bloqueio no firewall"
            }
    
    # ── 2. Bot Scanner Detection ──
    if not ameaca:
        for sig in BOT_SIGNATURES:
            if sig in user_agent:
                ameaca = {
                    "tipo": "BOT_SCANNER",
                    "severidade": "MÉDIA",
                    "descricao": f"Scanner/bot detectado: User-Agent contém '{sig}'",
                    "acao": "Verificar se é scan de segurança autorizado"
                }
                break
    
    # ── 3. Suspicious Path Probing ──
    if not ameaca:
        for sp in SUSPICIOUS_PATHS:
            if sp in path:
                ameaca = {
                    "tipo": "PATH_PROBING",
                    "severidade": "MÉDIA",
                    "descricao": f"Tentativa de acesso a caminho suspeito: {path}",
                    "acao": "IP pode estar mapeando a superfície de ataque"
                }
                break
    
    # ── 4. SQL Injection / XSS em URL ou Body (Pilar 13) ──
    url_completa = request_obj.url.lower()
    
    # Extrai o corpo do POST se houver
    post_data = ""
    if request_obj.method in ['POST', 'PUT', 'PATCH']:
        if request_obj.is_json:
            post_data = str(request_obj.get_json() or "").lower()
        else:
            post_data = str(dict(request_obj.form)).lower()
            
    sqli_xss_patterns = ["' or ", "union select", "drop table", "1=1", "waitfor delay", "benchmark(", "<script>", "javascript:"]
    for pat in sqli_xss_patterns:
        if pat in url_completa or pat in post_data:
            ameaca = {
                "tipo": "SQLI_XSS_ATTEMPT",
                "severidade": "ALTA",
                "descricao": f"Possível Injeção/XSS: padrão '{pat}' detectado (Pilar 13)",
                "acao": "Bloqueado pelo WAF Interno. Input deve usar input-sanitizer-translator."
            }
            break
    
    if ameaca:
        registro_ameaca = {
            "id": int(agora * 1000),
            "timestamp": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            "timestamp_raw": agora,
            "ip": ip,
            "user_agent": user_agent[:200],
            "metodo": request_obj.method,
            "path": request_obj.path,
            "url": request_obj.url[:500],
            **ameaca
        }
        with _lock:
            _threat_log.appendleft(registro_ameaca)
        threading.Thread(target=_salvar_logs).start()
        return registro_ameaca
    
    return None


# ════════════════════════════════════════════════════════
#  APIs DE CONSULTA (chamadas pelo frontend)
# ════════════════════════════════════════════════════════

def get_error_logs(limit=50, filtro_tipo=None):
    """Retorna os últimos N erros, com filtro opcional por tipo."""
    with _lock:
        logs = list(_error_log)
    
    if filtro_tipo:
        logs = [l for l in logs if l.get("erro_tipo") == filtro_tipo]
    
    return logs[:limit]


def get_threat_logs(limit=50):
    """Retorna os últimos N registros de ameaças detectadas."""
    with _lock:
        return list(_threat_log)[:limit]


def get_error_stats():
    """Retorna estatísticas agregadas dos erros capturados."""
    with _lock:
        erros = list(_error_log)
        ameacas = list(_threat_log)
    
    # Agrupa erros por tipo
    por_tipo = defaultdict(int)
    por_rota = defaultdict(int)
    por_status = defaultdict(int)
    
    for e in erros:
        por_tipo[e.get("erro_tipo", "?")] += 1
        por_rota[e.get("rota", "?")] += 1
        por_status[e.get("status_code", "?")] += 1
    
    # Agrupa ameaças por tipo
    ameacas_por_tipo = defaultdict(int)
    for a in ameacas:
        ameacas_por_tipo[a.get("tipo", "?")] += 1
    
    return {
        "total_erros": len(erros),
        "total_ameacas": len(ameacas),
        "erros_por_tipo": dict(sorted(por_tipo.items(), key=lambda x: x[1], reverse=True)),
        "erros_por_rota": dict(sorted(por_rota.items(), key=lambda x: x[1], reverse=True)[:10]),
        "erros_por_status": dict(por_status),
        "ameacas_por_tipo": dict(ameacas_por_tipo),
        "ultimo_erro": erros[0] if erros else None,
        "ultima_ameaca": ameacas[0] if ameacas else None
    }


def limpar_logs():
    """Limpa todos os logs da memória."""
    with _lock:
        _error_log.clear()
        _threat_log.clear()
        _request_counter.clear()
    return {"status": "success", "message": "Logs limpos com sucesso"}


def get_error_detail(error_id):
    """Retorna detalhes completos de um erro específico pelo ID."""
    with _lock:
        for e in _error_log:
            if e.get("id") == error_id:
                return e
    return None


# ════════════════════════════════════════════════════════
#  ANALISADOR DINÂMICO — Lê testes + código SEM modificar nada
#  Objetivo: compilar contexto para ajudar a consertar erros
#  Princípio: ZERO código injetado no sistema. Só leitura.
# ════════════════════════════════════════════════════════

import os
import re
import glob

# Raiz do projeto (detectada automaticamente)
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def analisar_falhas_teste(lista_falhas):
    """
    Recebe a lista de falhas dos testes unitários e analisa cada uma,
    rastreando pelo código-fonte (SOMENTE LEITURA) para compilar contexto.
    
    Entrada: lista de dicts com {pagina, rota, categoria, teste, detalhe}
    Saída: lista enriquecida com {caminho_codigo, contexto_compilado, pilar}
    
    IMPORTANTE: Esta função NÃO modifica nenhum arquivo. Apenas LÊ.
    """
    resultados = []
    
    for falha in lista_falhas:
        rota = falha.get("rota", "")
        categoria = falha.get("categoria", "")
        teste = falha.get("teste", "")
        detalhe = falha.get("detalhe", "")
        
        analise = {
            **falha,
            "caminho_codigo": [],
            "contexto_compilado": {},
            "pilar_violado": "",
            "severidade": "MÉDIA"
        }
        
        # 1. Encontrar o arquivo da rota
        rota_info = _localizar_rota_no_codigo(rota)
        if rota_info:
            analise["caminho_codigo"] = rota_info["caminho"]
            analise["arquivo_fonte"] = rota_info["arquivo"]
            analise["funcao_handler"] = rota_info["funcao"]
            analise["linha_handler"] = rota_info["linha"]
        
        # 2. Classificar o pilar violado pela categoria do teste
        analise["pilar_violado"] = _classificar_pilar(categoria, teste, detalhe)
        
        # 3. Classificar severidade
        analise["severidade"] = _classificar_severidade(categoria, teste)
        
        # 4. Compilar contexto (o que estava acontecendo naquela rota)
        analise["contexto_compilado"] = _compilar_contexto_rota(
            rota, rota_info, categoria, teste, detalhe
        )
        
        resultados.append(analise)
    
    return resultados


def _localizar_rota_no_codigo(rota):
    """
    Procura nos arquivos routes/*.py qual função serve a rota dada usando AST.
    SOMENTE LEITURA — não modifica nada.
    """
    if not rota:
        return None
    
    routes_dir = os.path.join(_PROJECT_ROOT, "routes")
    if not os.path.isdir(routes_dir):
        return None
    
    rota_limpa = rota.rstrip("/")
    
    for py_file in glob.glob(os.path.join(routes_dir, "*.py")):
        try:
            with open(py_file, "r", encoding="utf-8", errors="ignore") as f:
                codigo = f.read()
            tree = ast.parse(codigo)
        except:
            continue
            
        nome_arquivo = os.path.basename(py_file)
        
        for node in ast.walk(tree):
            # Procura por definição de função
            if isinstance(node, ast.FunctionDef):
                # Verifica os decorators da função
                for dec in node.decorator_list:
                    # Decorators de rota do flask (ex: @bp.route('/rota'))
                    if isinstance(dec, ast.Call) and isinstance(dec.func, ast.Attribute) and dec.func.attr == 'route':
                        if dec.args and isinstance(dec.args[0], ast.Constant):
                            rota_pattern = dec.args[0].value
                            rota_base = re.sub(r"<[^>]+>", "", rota_pattern).rstrip("/")
                            if rota_limpa == rota_base or rota_limpa.startswith(rota_base):
                                linha_funcao = node.lineno
                                
                                caminho = [
                                    {"passo": "Requisição HTTP", "detalhe": f"→ {rota}"},
                                    {"passo": f"routes/{nome_arquivo}", "detalhe": f"Decorator de Rota: @route('{rota_pattern}') na linha {linha_funcao - 1}"},
                                    {"passo": f"Handler: {node.name}()", "detalhe": f"Linha {linha_funcao}"}
                                ]
                                
                                # Extrai o corpo da função do código original
                                linhas = codigo.split('\n')
                                corpo = _ler_corpo_funcao(linhas, linha_funcao - 1)
                                if corpo:
                                    caminho.append({
                                        "passo": "Corpo da função",
                                        "detalhe": corpo[:200]
                                    })
                                
                                return {
                                    "caminho": caminho,
                                    "arquivo": f"routes/{nome_arquivo}",
                                    "funcao": node.name,
                                    "linha": linha_funcao
                                }
    return None


def _ler_corpo_funcao(linhas, inicio):
    """Lê o corpo de uma função Python a partir da linha de definição. SOMENTE LEITURA."""
    if inicio >= len(linhas):
        return None
    
    corpo = []
    indent_base = None
    
    for i in range(inicio + 1, min(inicio + 20, len(linhas))):
        linha = linhas[i]
        stripped = linha.rstrip()
        
        if not stripped:
            continue
        
        indent = len(linha) - len(linha.lstrip())
        if indent_base is None:
            indent_base = indent
        
        if indent < indent_base and stripped:
            break
        
        corpo.append(stripped)
    
    return " | ".join(corpo[:5])


def _classificar_pilar(categoria, teste, detalhe):
    """Classifica qual pilar TRPROC está sendo violado."""
    cat_lower = (categoria or "").lower()
    teste_lower = (teste or "").lower()
    
    mapa = {
        "sqli": "Pilar 13 (Sanitização Universal Anti-SQLi)",
        "xss": "Pilar 13 (Sanitização Universal Anti-XSS)",
        "csrf": "Pilar 3 (Autenticação/RBAC)",
        "rbac": "Pilar 3 (Autenticação/RBAC)",
        "cross-role": "Pilar 3 (Autenticação/RBAC)",
        "cookie": "Pilar 3 (Autenticação/RBAC)",
        "header": "Pilar 0 (Anti-Regressão)",
        "cors": "Pilar 3 (Autenticação/RBAC)",
        "redirect": "Pilar 0 (Anti-Regressão)",
        "crlf": "Pilar 0 (Anti-Regressão)",
        "overflow": "Pilar 5 (Formulários Dinâmicos)",
        "path": "Pilar 0 (Anti-Regressão) + Pilar 2 (Banco)",
        "ssti": "Pilar 13 (Sanitização Universal)",
        "fuzzing": "Pilar 13 (Sanitização Universal)",
        "formulário": "Pilar 5 (Formulários Dinâmicos)",
        "botão": "Pilar 10 (UX Premium)",
        "dependência": "Pilar 0 (Anti-Regressão)",
        "monstro": "Pilar 14 (Governança Monstro)",
        "import": "Pilar 14 (Governança Monstro)"
    }
    
    for chave, pilar in mapa.items():
        if chave in cat_lower or chave in teste_lower:
            return pilar
    
    return "Pilar 0 (Anti-Regressão)"


def _classificar_severidade(categoria, teste):
    """Define severidade da falha."""
    criticos = ["sqli", "csrf", "rbac", "cross-role", "path", "ssti"]
    altos = ["xss", "cookie", "cors", "crlf", "redirect", "header"]
    
    cat_lower = (categoria or "").lower()
    for c in criticos:
        if c in cat_lower:
            return "CRÍTICA"
    for a in altos:
        if a in cat_lower:
            return "ALTA"
    return "MÉDIA"


def _compilar_contexto_rota(rota, rota_info, categoria, teste, detalhe):
    """
    Compila todo o contexto necessário para entender e corrigir a falha.
    Lê código-fonte e templates SEM modificar nada.
    """
    contexto = {
        "o_que_aconteceu": "",
        "onde_no_codigo": "",
        "como_corrigir": "",
        "pilar_guia": ""
    }
    
    cat_lower = (categoria or "").lower()
    
    if "sqli" in cat_lower or "xss" in cat_lower or "ssti" in cat_lower:
        contexto["o_que_aconteceu"] = f"A rota {rota} foi reprovada na checagem de Segurança (Falta de Sanitização)"
        contexto["onde_no_codigo"] = rota_info["arquivo"] if rota_info else "Arquivo não localizado"
        contexto["como_corrigir"] = "⚠️ Ação Obrigatória: Rejeitar payload e utilizar a API `input-sanitizer-translator` antes de gravar/exibir os dados."
        contexto["pilar_guia"] = "Pilar 13: Nenhum input é confiável. Escape e limpe tudo."
        
    elif "csrf" in cat_lower:
        contexto["o_que_aconteceu"] = f"A rota {rota} aceitou requisição sem token CSRF válido"
        contexto["onde_no_codigo"] = rota_info["arquivo"] if rota_info else "Arquivo não localizado"
        contexto["como_corrigir"] = "Implementar validação de CSRF Token em todos os métodos POST/PUT/DELETE."
        contexto["pilar_guia"] = "Pilar 3: Autenticação/RBAC - Toda ação mutante requer verificação de identidade."
        
    elif "rbac" in cat_lower or "cross-role" in cat_lower:
        contexto["o_que_aconteceu"] = f"Quebra de Acesso (Privilégio Escalonado) em {rota}"
        contexto["onde_no_codigo"] = rota_info["arquivo"] if rota_info else "Arquivo não localizado"
        contexto["como_corrigir"] = "Revisar a matriz de permissões (`requires_auth(role)`) e certificar-se que os headers e fallback hierárquico estão mapeados."
        contexto["pilar_guia"] = "Pilar 3: Autenticação Restrita. Zero Trust."
        
    elif "monstro" in cat_lower or "import" in cat_lower:
        contexto["o_que_aconteceu"] = f"A importação de planilha apontou anomalias em {rota}"
        contexto["onde_no_codigo"] = rota_info["arquivo"] if rota_info else "Arquivo não localizado"
        contexto["como_corrigir"] = "Remover alias hardcoded. Garantir que a leitura do dicionário seja baseada na Tabela Mestre (`cadastros_dinamicos`)."
        contexto["pilar_guia"] = "Pilar 14: Governança do Monstro. Dados ditam a ingestão, não código sujo."
        
    else:
        contexto["o_que_aconteceu"] = f"Teste '{teste}' falhou na rota {rota}: {detalhe}"
        contexto["onde_no_codigo"] = rota_info["arquivo"] if rota_info else "Arquivo não localizado"
        contexto["como_corrigir"] = "Analisar o handler identificado via AST para corrigir o fluxo da página."
        contexto["pilar_guia"] = "Pilar 0: Anti-Regressão — corrigir sem quebrar lógica legado."
    
    return contexto


def registrar_falha_teste(pagina, rota, categoria, teste, detalhe):
    """
    Injeta uma falha de teste automatizado no log de erros.
    Chamado pelo Nuclear Scanner para alimentar o Dashboard de Debug.
    """
    agora = datetime.now()
    registro = {
        "id": int(agora.timestamp() * 1000),
        "timestamp": agora.strftime("%d/%m/%Y %H:%M:%S"),
        "timestamp_raw": agora.timestamp(),
        "tipo": "teste_auto",
        "status_code": 0,
        "metodo": "SCAN",
        "rota": rota,
        "url_completa": f"[AUTO-TEST] {pagina}",
        "ip": "127.0.0.1",
        "user_agent": "TRPROC Nuclear Scanner v2.0",
        "erro_tipo": categoria,
        "erro_msg": f"[{categoria}] {teste}: {detalhe}"[:500],
        "caminho_debug": [{"arquivo": "unit_test_runner.py", "funcao": "nuclear_scan", "linha": 0, "codigo": teste}],
        "traceback_completo": f"Teste: {teste}\nDetalhe: {detalhe}\nPágina: {pagina}\nCategoria: {categoria}",
        "query_params": {},
        "form_data_keys": [],
    }
    with _lock:
        _error_log.appendleft(registro)
    _salvar_logs()
