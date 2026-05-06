# Tarefa: Refatoração Arquitetural do Backend Python (TRPROC)

**Status Atual:** 🕒 Planejado / Aguardando Execução
**Data de Criação:** 2026-04-29
**Objetivo:** Resolver anti-padrões de arquitetura (Fat Routes, Bloated Models, Misplaced Files) para garantir maior estabilidade, facilidade de manutenção e segurança na evolução do TRPROC.

---

## 📝 Plano de Execução em 3 Níveis

### Nível 1: Limpeza de Lixo Operacional e Arquivos Mal Posicionados
**Risco:** Baixo (Resolve "ModuleNotFoundError" com testes rápidos de importação).
**Tempo Estimado:** 5 a 10 minutos.
- [ ] Apagar arquivos de backup mortos (`routes/client_form_restored.py` e `routes/client_form_restored_partial.py`).
- [ ] Mover `routes/deploy_controller.py` para `controllers/deploy_controller.py`.
- [ ] Mover `utils/keycloak_service.py` para `services/keycloak_service.py`.
- [ ] Executar varredura global (`grep_search`) e corrigir todas as strings de importação afetadas pelas mudanças acima.
- [ ] Reiniciar o Flask e validar estabilidade na tela de login e rotas afetadas.

### Nível 2: Desacoplamento do Banco de Dados (Bloated Models)
**Risco:** Moderado (Requer mapeamento cirúrgico de tabelas e relacionamentos).
**Tempo Estimado:** 30 a 45 minutos.
- [ ] Quebrar o arquivo gigante `models/core_models.py` em arquivos menores, focados no domínio:
  - `models/usuarios.py` (Tenant, Usuarios, Autenticacao)
  - `models/processos.py` (Processos, Dossiê, Tramitação)
  - `models/formularios.py` (Dinâmico, Regras, Consumo)
- [ ] Criar o arquivo `models/__init__.py` para agregar todos os módulos menores e exportar como se fossem um único pacote.
- [ ] Testar a injeção do banco em diferentes rotas e migrações.

### Nível 3: Emagrecimento das Rotas Obesas (Fat Routes)
**Risco:** Alto (Efeito dominó, exige testes unitários e manuais consistentes).
**Tempo Estimado:** Múltiplas sessões de ~30 minutos por funcionalidade crítica (Total ~3 a 4 horas).
- [ ] Escolher uma rota por vez (Exemplo: `/processo/<id>/autos` em `api_dossie.py`).
- [ ] Extrair queries complexas (`db.session.execute`) e lógica de negócio.
- [ ] Mover essas lógicas para controladores centralizados (ex: `controllers/dossie_controller.py`).
- [ ] Manter os arquivos de rota (`api_dossie.py`, `client_form.py`) contendo apenas: recebimento de requisição -> chamada do controlador -> retorno JSON ou renderização de template.
- [ ] Validar a funcionalidade isolada no frontend antes de mover para a próxima rota.

---
**Observações:**
A execução do Nível 1 foi colocada "em pausa" a pedido do usuário em 29/04/2026. Este documento servirá de guia exato quando ele decidir retomar os trabalhos.
