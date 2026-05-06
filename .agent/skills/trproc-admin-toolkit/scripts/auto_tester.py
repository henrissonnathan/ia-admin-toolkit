import requests
import json
import time

BASE_URL = "http://127.0.0.1:5001/admin/estudio"

TIPOS_PERGUNTAS = [
    "texto", "numero", "texto_longo", "radio", "checkbox", "select", 
    "tabela_dinamica", "matriz", "data", "upload", "bloco_texto"
]

def criar_pergunta(session, texto, tipo="texto"):
    payload = {
        "texto": texto,
        "tipo": tipo,
        "opcoes": "Opcao A, Opcao B" if tipo in ['radio', 'checkbox', 'select'] else "",
        "id_fase": 1,
        "visibilidade": "publica"
    }
    res = session.post(f"{BASE_URL}/perguntas", json=payload)
    if res.status_code in [200, 201]:
        return res.json().get('id')
    return None

def salvar_regras(session, id_origem, regras):
    res = session.post(f"{BASE_URL}/perguntas/{id_origem}/regras", json={"regras": regras})
    return res.status_code == 200

def rodar_teste_inteligente():
    print("=== INICIANDO TESTE ESTRUTURADO DE MÚLTIPLAS FASES ===")
    session = requests.Session()
    
    # FASE 1: CRIAR BASE DE PERGUNTAS (1 DE CADA TIPO)
    print("\n[FASE 1] Criando um catálogo de perguntas base (uma de cada tipo)...")
    ids_base = {}
    for tipo in TIPOS_PERGUNTAS:
        pid = criar_pergunta(session, f"Base - {tipo.upper()}", tipo)
        if pid:
            ids_base[tipo] = pid
            print(f"  -> Criada: {tipo} (ID {pid})")
            
    # FASE 2: TESTES ISOLADOS DE REGRAS
    print("\n[FASE 2] Testando Regras Separadas (1 para 1)...")
    # Mostrar
    id_cond_mostrar = criar_pergunta(session, "[Teste Isolado] Controle Mostrar", "radio")
    id_alvo_mostrar = criar_pergunta(session, "[Teste Isolado] Alvo a ser Mostrado", "texto")
    if id_cond_mostrar and id_alvo_mostrar:
        salvar_regras(session, id_cond_mostrar, [{"id_pergunta_condicao": id_cond_mostrar, "operador": "igual", "valor_condicao": "Opcao A", "acao": "mostrar", "id_pergunta_alvo": id_alvo_mostrar}])
        print("  -> Regra MOSTRAR isolada criada.")

    # Ocultar
    id_cond_ocultar = criar_pergunta(session, "[Teste Isolado] Controle Ocultar", "radio")
    id_alvo_ocultar = criar_pergunta(session, "[Teste Isolado] Alvo a ser Ocultado", "texto")
    if id_cond_ocultar and id_alvo_ocultar:
        salvar_regras(session, id_cond_ocultar, [{"id_pergunta_condicao": id_cond_ocultar, "operador": "igual", "valor_condicao": "Opcao A", "acao": "ocultar", "id_pergunta_alvo": id_alvo_ocultar}])
        print("  -> Regra OCULTAR isolada criada.")

    # FASE 3: TESTE DE CONFLITO DE REGRAS (A PROVA DE FOGO)
    print("\n[FASE 3] Teste de Conflito (Múltiplas regras mirando no mesmo alvo)...")
    id_alvo_conflito = criar_pergunta(session, "[Teste Conflito] Serei Mostrado ou Ocultado?", "texto")
    id_controle_1 = criar_pergunta(session, "[Teste Conflito] Botão 1 (Manda Mostrar)", "radio")
    id_controle_2 = criar_pergunta(session, "[Teste Conflito] Botão 2 (Manda Ocultar)", "radio")
    
    if id_alvo_conflito and id_controle_1 and id_controle_2:
        # Controle 1 manda Mostrar se for "Opcao A"
        salvar_regras(session, id_controle_1, [{"id_pergunta_condicao": id_controle_1, "operador": "igual", "valor_condicao": "Opcao A", "acao": "mostrar", "id_pergunta_alvo": id_alvo_conflito}])
        # Controle 2 manda Ocultar se for "Opcao B"
        salvar_regras(session, id_controle_2, [{"id_pergunta_condicao": id_controle_2, "operador": "igual", "valor_condicao": "Opcao B", "acao": "ocultar", "id_pergunta_alvo": id_alvo_conflito}])
        print("  -> Conflito criado! Duas perguntas controlam a mesma pergunta alvo com ordens inversas.")
        
    print("\n=== TESTES INJETADOS COM SUCESSO ===")
    print("Por favor, abra o Formulário e teste clicar nos 'Testes de Conflito' para ver quem vence a prioridade.")

if __name__ == "__main__":
    rodar_teste_inteligente()
