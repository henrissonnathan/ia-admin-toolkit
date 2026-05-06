---
name: task-analysis-governor
description: OBRIGATÓRIO para rastrear progresso, registrar análises técnicas de arquivos e impedir loops de tarefas repetitivas. Use esta skill para manter um histórico de "quem fez o quê" e evitar desfazer ou repetir correções.
---

# Task & Analysis Governor

Esta skill garante a soberania da informação técnica e impede loops de desenvolvimento.

## Fluxo de Trabalho Obrigatório

1. **Antes de Modificar**: Verifique o arquivo de tarefas (`.agents/records/tasks/current_task.md`) e os registros de análise (`.agents/records/analysis/`).
2. **Análise de Arquivo**: Para cada arquivo importante analisado, crie ou atualize um registro em `.agents/records/analysis/[nome_do_arquivo].md`.
3. **Mapeamento de Mudanças**: Documente cada alteração (adição, remoção, correção) no log de tarefas.

## Estrutura de Pastas

- `.agents/records/tasks/`: Lista de tarefas e status.
- `.agents/records/analysis/`: Arquivos MD contendo a lógica interna, dependências e "pegadinhas" de cada arquivo do código-fonte.

## Regras Anti-Loop

- NUNCA repita uma correção documentada como [x] concluída.
- Se encontrar um problema recorrente, consulte a análise do arquivo correspondente para entender por que a solução anterior falhou.
