---
name: agent-tracker
description: OBRIGATÓRIO para rastrear o progresso do agente, registrar análises técnicas detalhadas e impedir loops de tarefas repetitivas. Use esta skill no início de cada tarefa complexa para mapear o estado atual e registrar cada arquivo modificado ou analisado.
---

# Agent Tracker (Rastreador de Progresso)

Esta skill é uma ferramenta de governança para garantir que o agente não execute as mesmas tarefas repetidamente e mantenha um histórico claro de todas as análises e modificações.

## Diretrizes de Uso

Sempre que iniciar uma nova tarefa ou modificação, você deve:

1.  **Mapear o Estado Atual**: Antes de qualquer modificação, crie ou atualize um arquivo de tarefa em `.agents/records/tasks/task_[ID].md`.
2.  **Registrar Análises**: Para cada arquivo importante analisado, crie um registro em `.agents/records/analyses/[filename].analysis.md`. Isso evita ter que reler o arquivo inteiro em turnos futuros.
3.  **Prevenir Loops**: Antes de tentar uma solução que falhou anteriormente (registrada no histórico), você deve obrigatoriamente mudar a abordagem.
4.  **Sincronizar com o Usuário**: Informe ao usuário quando um marco for atingido usando os registros como referência.

## Estrutura de Arquivos

- **Tasks**: `.agents/records/tasks/`
  - Deve conter o objetivo, arquivos envolvidos, status de cada etapa e impedimentos.
- **Analyses**: `.agents/records/analyses/`
  - Deve conter:
    - Caminho do arquivo.
    - Resumo técnico das funções/lógica principal.
    - Pontos de falha identificados.
    - Data da última análise.

## Protocolo de "Não-Repetição"

Se uma tarefa falhar ou o usuário reportar que nada mudou:

1.  Consulte o log de análise do arquivo em questão.
2.  Verifique se houve erro de cache ou deploy (mencionado pelo usuário no passado).
3.  Tente uma abordagem radicalmente diferente ou adicione logs de depuração mais profundos antes de repetir a mesma lógica.
