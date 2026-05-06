from functools import wraps
from flask import request, jsonify, session, redirect, url_for
import jwt
from models.core_models import Configuracao
import os
from configs.roles_config import ROLES_LICITAPRO, EMAILS_SUPER_ADMIN, check_super_admin, get_nivel_nome

# Simulador de Ambiente de Dev (Para não precisar do Keycloak 100% online)
# Pode ser 'admin', 'cliente' ou 'none'
DEV_MOCK_ROLE = os.getenv('DEV_MOCK_ROLE', 'none')

def get_keycloak_public_key():
    # Em produção, isso faria fetch da chave pública real do Keycloak:
    # http://localhost:8080/realms/licitapro/protocol/openid-connect/certs
    # Para o MVP, mockamos se a chave real não estiver no banco.
    return "MOCK_PUBLIC_KEY"

def requires_auth(role=None, modulo_id=None):
    """
    Decorador (Leão de Chácara) para proteger rotas do Flask.
    Uso: @requires_auth(role='admin') ou @requires_auth(modulo_id='estudio_form')
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            
            # 1. SIMULADOR DE DESENVOLVIMENTO (Dev Bypass)
            # Prioridade 1: Override via sessão (Test Hub)
            if session.get('test_role_override'):
                # Se for super_admin ou admin, permitimos tudo no dev
                role_simulada = session.get('test_role_override', 'cliente')
                if role == 'admin' and role_simulada != 'admin':
                     return "Acesso Negado (Simulador): Esta tela é de Admin.", 403
                return f(*args, **kwargs)

            # Prioridade 2: Override via Env Var (Antigo)
            if DEV_MOCK_ROLE != 'none':
                if role == 'admin' and DEV_MOCK_ROLE != 'admin':
                    return "Acesso Negado (Simulador): Esta tela é de Admin.", 403
                return f(*args, **kwargs)

            # 2. PRODUÇÃO: Busca o Token
            auth_header = request.headers.get('Authorization')
            token = None
            
            if auth_header and auth_header.startswith('Bearer '):
                token = auth_header.split(" ")[1]
            elif 'jwt_token' in session:
                token = session['jwt_token']
                
            if not token:
                if request.is_json or request.path.startswith('/api/'):
                    return jsonify({'status': 'error', 'message': 'Token Keycloak Ausente'}), 401
                return redirect(url_for('auth.login'))

            # 3. VALIDAÇÃO DO JWT KEYCLOAK E RBAC
            try:
                payload = jwt.decode(token, options={"verify_signature": False})
                
                realm_access = payload.get('realm_access', {})
                user_roles = realm_access.get('roles', [])
                email = payload.get('email', '')
                
                roles_str = str(user_roles).lower()
                user_roles_lower = [str(r).lower() for r in user_roles]
                
                # OVERRIDE: Equipe LicitaPRO tem bypass do gate role_trproc
                # Usa Fonte Única de Verdade (configs/roles_config.py) — Pilar 3
                is_super_admin = check_super_admin(email, user_roles_lower)
                
                if not is_super_admin:
                    # Todos os usuários de TRPROC DEVEM ter a role_trproc para usar o sistema
                    if 'role_trproc' not in user_roles_lower:
                        return "Acesso Negado 403: Você não possui a permissão 'role_trproc' para acessar este sistema. Procure a central de acessos.", 403

                    # Checagem baseada na Matriz RBAC se modulo_id for especificado
                    if modulo_id:
                        from models.core_models import RBACMatriz
                        # Nível via Fonte Única (configs/roles_config.py) — Pilar 3
                        nivel_usuario = get_nivel_nome(user_roles_lower)
                        
                        regra = RBACMatriz.query.filter_by(nivel_nome=nivel_usuario, modulo_id=modulo_id).first()
                        
                        if not regra or not regra.pode_ver:
                            return "Acesso Negado 403: Seu perfil não tem permissão na Matriz RBAC para acessar este módulo.", 403
                    
                    # Checagem de role hardcoded legado (fallback)
                    elif role:
                        # Ignora cliente_leitura pois já exigimos role_trproc acima
                        if role == 'cliente_leitura':
                            pass
                            
                        elif role == 'master':
                            return "Acesso Negado 403: Acesso restrito a Master/Desenvolvedores.", 403
                        
                        elif role == 'admin':
                            tem_privilegio_admin = any(r in roles_str for r in ['admin', 'administrador', 'admin_licitacao'])
                            if not tem_privilegio_admin:
                                return "Acesso Negado 403: Acesso restrito a Administradores (Admin).", 403
                                
                        else:
                            if role.lower() not in roles_str:
                                return f"Acesso Negado 403: Privilégio '{role}' obrigatório não encontrado no token.", 403

                request.user_data = payload
                
            except jwt.ExpiredSignatureError:
                return jsonify({'status': 'error', 'message': 'Token Expirado. Faça login novamente.'}), 401
            except jwt.InvalidTokenError:
                return jsonify({'status': 'error', 'message': 'Token Inválido ou Corrompido.'}), 401
                
            return f(*args, **kwargs)
        return decorated_function
    return decorator
