import json
import uuid
from extensions import db
from sqlalchemy import text
from models.core_models import Municipio, UnidadeAdministrativa, Responsavel, UsuarioCliente, Registro

def generate_mock_data(num_muns=10, admins_per_mun=5, users_per_mun=5, procs_per_mun=50):
    """Gera massa de dados massiva para o módulo de testes Chaos/Sandbox."""
    print(f"Iniciando geração de massa de dados [TESTE] - Muns: {num_muns}, Procs/Mun: {procs_per_mun}")
    
    for m in range(1, num_muns + 1):
        mun_nome = f'[TESTE] Municipio {m}'
        mun = Municipio.query.filter_by(nome=mun_nome).first()
        if not mun:
            mun = Municipio(
                nome=mun_nome,
                status='ativo',
                is_sandbox=True,
                max_usuarios_n1=50,
                max_usuarios_n2=100,
                limite_processos_dia=500,
                limite_processos_mes=5000,
                limite_processos_ano=50000
            )
            db.session.add(mun)
            db.session.flush()

        # Criar Admins para o Municipio
        for a in range(1, admins_per_mun + 1):
            admin_user = f'admin_teste_{m}_{a}'
            admin = UsuarioCliente.query.filter_by(usuario=admin_user).first()
            if not admin:
                admin = UsuarioCliente(
                    usuario=admin_user,
                    nome_completo=f'[TESTE] Admin {a} (Mun {m})',
                    senha='senha_padrao_teste',
                    nivel='admin',
                    municipio_id_fk=mun.id,
                    status='ativo'
                )
                db.session.add(admin)

        # Criar Clientes (Usuários comuns)
        for c in range(1, users_per_mun + 1):
            cli_user = f'cliente_teste_{m}_{c}'
            cli = UsuarioCliente.query.filter_by(usuario=cli_user).first()
            if not cli:
                cli = UsuarioCliente(
                    usuario=cli_user,
                    nome_completo=f'[TESTE] Cliente {c} (Mun {m})',
                    senha='senha_padrao_teste',
                    nivel='cliente',
                    municipio_id_fk=mun.id,
                    status='ativo'
                )
                db.session.add(cli)

        db.session.flush() # Garantir que usuarios tem ID
        admin_id = UsuarioCliente.query.filter_by(usuario=f'admin_teste_{m}_1').first().id

        # Criar Processos Massivos
        for p in range(1, procs_per_mun + 1):
            try:
                db.session.execute(
                    text("""
                        INSERT INTO registros (id_protocolo, ano, usuario_id_fk, municipio_id_fk, 
                            status_id_fk, object, data_envio, chaveS)
                        VALUES (:protocolo, :ano, :usuario, :municipio, :status, :object, NOW(), '0')
                    """),
                    {
                        "protocolo": mun.id * 10000 + p,
                        "ano": 2026,
                        "usuario": admin_id,
                        "municipio": mun.id,
                        "status": 1,
                        "object": json.dumps({
                            "titulo": f"[TESTE] Processo Chaos {p} - {mun.nome}",
                            "is_test": True
                        }, ensure_ascii=False)
                    }
                )
            except Exception:
                pass  # Ignora se já existe (duplicate)

    db.session.commit()
    print("Massa de dados Chaos gerada com sucesso!")
    return True

def cleanup_mock_data():
    """Remove todos os dados e tramitações marcados como [TESTE]."""
    print("Iniciando limpeza massiva de dados [TESTE]...")
    
    # 1. Deleta tramitações (processo_hub_comunicacao) que pertencem a registros de teste
    try:
        db.session.execute(
            text("""
                DELETE h FROM processo_hub_comunicacao h
                JOIN registros r ON r.id = h.registro_id_fk
                WHERE r.object LIKE '%[TESTE]%'
            """)
        )
    except Exception:
        pass
        
    # 2. Excluindo Registros de teste
    try:
        db.session.execute(
            text("DELETE FROM registros WHERE object LIKE '%[TESTE]%'")
        )
    except Exception:
        pass
        
    # 3. Excluindo Usuários
    UsuarioCliente.query.filter(UsuarioCliente.nome_completo.like('[TESTE]%')).delete(synchronize_session=False)
    
    # 4. Excluindo Responsáveis e Unidades
    Responsavel.query.filter(Responsavel.nome.like('[TESTE]%')).delete(synchronize_session=False)
    UnidadeAdministrativa.query.filter(UnidadeAdministrativa.nome_secretaria.like('[TESTE]%')).delete(synchronize_session=False)
    
    # 5. Excluindo Municípios
    Municipio.query.filter(Municipio.nome.like('[TESTE]%')).delete(synchronize_session=False)
    
    db.session.commit()
    print("Limpeza do Sandbox/Chaos concluída com sucesso!")
    return True

