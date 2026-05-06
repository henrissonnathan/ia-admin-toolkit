import concurrent.futures
import random
import time
from sqlalchemy import text
from extensions import db
from flask import current_app
from traceback import format_exc

def _executar_trilha_admin(app_context_wrapper, engine, admin_id, mun_id, proc_ids, num_mensagens):
    """
    Simula um administrador enviando mensagens e alterando o status dos processos do seu município.
    Usamos o engine diretamente para maximizar o estresse e testar o pool de conexões (Pilar 13).
    """
    sucessos = 0
    erros = 0
    mensagens_erro = []
    
    with engine.connect() as conn:
        for i in range(num_mensagens):
            try:
                proc_id = random.choice(proc_ids)
                
                # 1. Enviar Mensagem (Simulando Dossiê / Hub)
                msg_content = f"[CHAOS ADMIN] Mensagem de estresse {i+1} do admin {admin_id}"
                
                conn.execute(
                    text("""
                        INSERT INTO processo_hub_comunicacao 
                        (registro_id_fk, autor_nome, conteudo, tipo)
                        VALUES (:reg, :autor, :msg, 'tramite_interno')
                    """),
                    {"reg": proc_id, "autor": f"AdminChaos_{admin_id}", "msg": msg_content}
                )
                
                # 2. 30% de chance de mudar o status do processo (Race Condition)
                if random.random() < 0.3:
                    novo_status = random.randint(1, 4)
                    conn.execute(
                        text("UPDATE registros SET status_id_fk = :status WHERE id = :reg"),
                        {"status": novo_status, "reg": proc_id}
                    )
                
                conn.commit()
                sucessos += 1
                
                # Pausa randômica muito curta para emular rede/processamento assíncrono real
                time.sleep(random.uniform(0.01, 0.05))
                
            except Exception as e:
                conn.rollback()
                erros += 1
                mensagens_erro.append(str(e))
                
    return {"tipo": "admin", "id": admin_id, "sucessos": sucessos, "erros": erros, "logs": mensagens_erro[:5]}

def _executar_trilha_cliente(app_context_wrapper, engine, cli_id, mun_id, proc_ids, num_mensagens):
    """
    Simula um cliente (requerente) enviando mensagens nos seus processos.
    """
    sucessos = 0
    erros = 0
    mensagens_erro = []
    
    with engine.connect() as conn:
        for i in range(num_mensagens):
            try:
                proc_id = random.choice(proc_ids)
                
                msg_content = f"[CHAOS CLIENTE] Mensagem de estresse {i+1} do cliente {cli_id}"
                
                # Cliente apenas posta no Hub (na visão externa)
                conn.execute(
                    text("""
                        INSERT INTO processo_hub_comunicacao 
                        (registro_id_fk, autor_nome, conteudo, tipo)
                        VALUES (:reg, :autor, :msg, 'msg_publica')
                    """),
                    {"reg": proc_id, "autor": f"ClienteChaos_{cli_id}", "msg": msg_content}
                )
                
                conn.commit()
                sucessos += 1
                
                time.sleep(random.uniform(0.01, 0.05))
                
            except Exception as e:
                conn.rollback()
                erros += 1
                mensagens_erro.append(str(e))
                
    return {"tipo": "cliente", "id": cli_id, "sucessos": sucessos, "erros": erros, "logs": mensagens_erro[:5]}


def disparar_estresse_tramitacao(num_threads=10, mensagens_por_thread=20):
    """
    Aciona o motor de caos. Coleta todos os processos de [TESTE] e despacha
    threads simulando os usuários.
    """
    try:
        # Obter os IDs de teste
        muns_teste = db.session.execute(text("SELECT id FROM municipios WHERE nome LIKE '%[TESTE]%'")).fetchall()
        if not muns_teste:
            return {"status": "error", "message": "Nenhum município [TESTE] encontrado. Gere a massa primeiro."}
            
        mun_ids = [m[0] for m in muns_teste]
        
        procs_teste = db.session.execute(text("SELECT id, municipio_id_fk FROM registros WHERE object LIKE '%[TESTE]%'")).fetchall()
        if not procs_teste:
            return {"status": "error", "message": "Nenhum processo [TESTE] encontrado. Gere a massa primeiro."}
            
        # Agrupar processos por município
        procs_by_mun = {}
        for p in procs_teste:
            mun_fk = p[1]
            if mun_fk not in procs_by_mun:
                procs_by_mun[mun_fk] = []
            procs_by_mun[mun_fk].append(p[0])
            
        # Preparar dados de threads
        tasks = []
        app = current_app._get_current_object()
        engine = db.engine # Usamos o motor SQLAlchemy diretamente para injetar em threads
        
        # Para cada município, vamos pegar os admins e clientes de teste
        usuarios_teste = db.session.execute(
            text("SELECT id, municipio_id_fk, nivel FROM usuarios_clientes WHERE nome_completo LIKE '%[TESTE]%' AND nivel IN ('admin', 'cliente')")
        ).fetchall()
        
        # Organizar usuarios
        for u in usuarios_teste:
            u_id = u[0]
            u_mun = u[1]
            u_nivel = u[2]
            
            # Se não houver processos pro municipio, ignora
            if u_mun not in procs_by_mun or not procs_by_mun[u_mun]:
                continue
                
            p_ids = procs_by_mun[u_mun]
            
            # Definimos as tasks
            if u_nivel == 'admin':
                tasks.append( (u_id, u_mun, p_ids, 'admin') )
            else:
                tasks.append( (u_id, u_mun, p_ids, 'cliente') )
                
        # Limitar número de threads ativas caso haja centenas de usuários
        tasks = tasks[:num_threads]
        if not tasks:
             return {"status": "error", "message": "Nenhuma task pôde ser gerada."}

        resultados = []
        
        print(f"Iniciando Chaos Engine com {len(tasks)} atores em paralelo (ThreadPool)...")
        
        # Executar em Paralelo
        with concurrent.futures.ThreadPoolExecutor(max_workers=min(len(tasks), 50)) as executor:
            futuros = []
            for t in tasks:
                u_id, u_mun, p_ids, t_tipo = t
                if t_tipo == 'admin':
                    futuros.append(executor.submit(_executar_trilha_admin, app, engine, u_id, u_mun, p_ids, mensagens_por_thread))
                else:
                    futuros.append(executor.submit(_executar_trilha_cliente, app, engine, u_id, u_mun, p_ids, mensagens_por_thread))
                    
            for future in concurrent.futures.as_completed(futuros):
                try:
                    res = future.result()
                    resultados.append(res)
                except Exception as exc:
                    resultados.append({"status": "fatal_error", "erro": str(exc)})
                    
        total_sucessos = sum([r.get('sucessos', 0) for r in resultados if 'sucessos' in r])
        total_erros = sum([r.get('erros', 0) for r in resultados if 'erros' in r])
        
        return {
            "status": "success",
            "message": "Execução Chaos finalizada.",
            "atores_threads": len(tasks),
            "mensagens_enviadas": total_sucessos,
            "erros_corridos": total_erros,
            "detalhes": resultados
        }
        
    except Exception as e:
        import traceback
        return {"status": "error", "message": str(e), "traceback": traceback.format_exc()}
