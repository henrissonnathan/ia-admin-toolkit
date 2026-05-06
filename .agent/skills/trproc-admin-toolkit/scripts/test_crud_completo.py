# -*- coding: utf-8 -*-
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from TRPROC_WEB import app
from extensions import db
from models.core_models import PerguntaDinamica, RegraCondicional, CondicaoDeRegra
import json
import traceback

TIPOS_PERGUNTAS = [
    'texto', 'numero', 'texto_longo', 'radio', 'checkbox', 'select', 
    'tabela_dinamica', 'matriz', 'data', 'upload', 'bloco_texto'
]

def run_test():
    with app.app_context():
        try:
            print("=== INICIANDO TESTE CRUD COMPLETO ===")
            ids_criados = []
            
            print("\n[FASE 1] Criando perguntas...")
            for idx, tipo in enumerate(TIPOS_PERGUNTAS):
                opcoes = "A, B" if tipo in ['radio', 'checkbox', 'select'] else ""
                p = PerguntaDinamica(
                    label=f"Teste CRUD - {tipo}",
                    campo_id=f"test_crud_{tipo}_{idx}",
                    tipo=tipo,
                    opcoes=opcoes,
                    status="ativo"
                )
                db.session.add(p)
                db.session.flush() # Pega ID
                ids_criados.append(p.id)
                print(f" -> Criada pergunta tipo {tipo} (ID: {p.id})")
            
            print("\n[FASE 2] Criando regras...")
            
            if len(ids_criados) >= 2:
                regra1 = RegraCondicional(
                    pergunta_alvo_id=ids_criados[0],
                    tipo_acao=json.dumps({"acao": "mostrar"}),
                    logica_condicao='QUALQUER'
                )
                db.session.add(regra1)
                db.session.flush()
                
                cond1 = CondicaoDeRegra(
                    regra_id=regra1.id,
                    pergunta_gatilho_id=ids_criados[1],
                    operador='==',
                    valor_gatilho='Teste'
                )
                db.session.add(cond1)
                print(" -> Criada Regra MOSTRAR")
                
                regra2 = RegraCondicional(
                    pergunta_alvo_id=ids_criados[1],
                    tipo_acao=json.dumps({"acao": "esconder"}),
                    logica_condicao='TODAS'
                )
                db.session.add(regra2)
                db.session.flush()
                
                cond2 = CondicaoDeRegra(
                    regra_id=regra2.id,
                    pergunta_gatilho_id=ids_criados[0],
                    operador='!=',
                    valor_gatilho='X'
                )
                db.session.add(cond2)
                print(" -> Criada Regra ESCONDER")
            
            db.session.commit()
            print("\n[SUCESSO] Base de teste criada e commitada.")
            
            print("\n[FASE 3] Testando Exclusao...")
            
            for pid in ids_criados:
                print(f" -> Excluindo pergunta ID: {pid}")
                p = PerguntaDinamica.query.get(pid)
                if p:
                    p.status = 'inativo'
                    db.session.commit()
            
            print("\n[SUCESSO] Todas as exclusoes logicas passaram!")
            
            print("\n[RELATORIO] Verificando regras orfas (regras que apontam para perguntas inativas)...")
            regras_orfas = 0
            todas_regras = RegraCondicional.query.all()
            for r in todas_regras:
                alvo = PerguntaDinamica.query.get(r.pergunta_alvo_id)
                if alvo and alvo.status == 'inativo':
                    regras_orfas += 1
                    print(f" -> ALERTA: Regra {r.id} aponta para pergunta alvo inativa ({alvo.id})!")
                
                for c in r.condicoes:
                    gatilho = PerguntaDinamica.query.get(c.pergunta_gatilho_id)
                    if gatilho and gatilho.status == 'inativo':
                        regras_orfas += 1
                        print(f" -> ALERTA: Condicao {c.id} aponta para pergunta gatilho inativa ({gatilho.id})!")
            
            if regras_orfas > 0:
                print(f"\n[FALHA DE INTEGRIDADE] Encontradas {regras_orfas} referencias para perguntas inativas!")
                print("Isso causa quebra no formulario client-side (frontend) e erros no MotorRegras!")
                print("O erro do usuario 'tento escluir uma pergunta e deu erro' acontece pq as regras orfas nao sao excluidas / inativadas quando a pergunta inativa!")
            else:
                print("\n[INTEGRIDADE OK] Nenhuma regra orfa encontrada.")
                
            
        except Exception as e:
            db.session.rollback()
            print(f"\n[ERRO CRITICO] Ocorreu um erro no CRUD: {str(e)}")
            traceback.print_exc()

if __name__ == '__main__':
    run_test()
