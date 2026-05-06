---
name: trproc-admin-toolkit
description: Ferramentas avançadas de administração, diagnóstico e testes automatizados do TRPROC. Utilize esta skill sempre que o usuário solicitar auditorias de integridade, testes de CRUD de formulários, limpeza de dados órfãos, diagnósticos de banco de dados ou ferramentas de suporte que operam fora do fluxo principal da aplicação. Garante a estabilidade do sistema após migrações ou atualizações de branch.
---

# TRPROC Admin Toolkit

Este módulo centraliza ferramentas de governança técnica e diagnóstico profundo para garantir que o sistema TRPROC permaneça estável e íntegro, especialmente durante transições de branch e atualizações de schema.

## Quando Usar
- **Auditoria de Integridade**: Realizar verificações de regras órfãs ou dados inconsistentes.
- **Testes de Fluxo (CRUD)**: Validar se as operações de criação, edição e exclusão no Estúdio estão funcionando corretamente.
- **Diagnóstico Pós-Migração**: Gerar relatórios técnicos após realizar `git clone` ou trocar de branch.
- **Validação de Motor**: Testar o comportamento do 'Motor Monstro' e do motor de regras sob condições específicas.

## Estrutura de Portabilidade
As ferramentas foram migradas da pasta raiz `ai_tools/` para o diretório de scripts desta skill para garantir que permaneçam funcionais e portáteis.

### Localização dos Scripts
Os scripts estão em: `.agents/skills/trproc-admin-toolkit/scripts/`

1.  **`test_crud_completo.py`**: Simulador de preenchimento e exclusão de todos os tipos de perguntas.
2.  **`ast_scanner.py`**: Analisador estático para detecção de vulnerabilidades e padrões obsoletos.
3.  **`db_schema_mini.py`**: Validador de conformidade de schema SQL.
4.  **`auto_tester.py`**: Motor de execução de testes E2E automatizados.
5.  **`setup_portability.py`**: Script para reconfigurar caminhos locais após um novo clone.

## Fluxo de Trabalho (Workflow)

### 1. Diagnóstico Inicial
Sempre execute o `test_crud_completo.py` se houver suspeita de instabilidade no Estúdio.
- **Ação**: `python .agents/skills/trproc-admin-toolkit/scripts/test_crud_completo.py`

### 2. Auditoria de Código
Use o `ast_scanner.py` antes de realizar grandes refatorações.

### 3. Geração de Relatório
Ao finalizar qualquer ação, gere um artefato seguindo este padrão:

# Relatório de Governança TRPROC
## Status: [OK / FALHA]
## Ferramenta Utilizada: [Nome]
## Diagnóstico:
- Resumo dos achados técnicos.
## Ações de Correção:
- O que foi alterado para estabilizar o sistema.

> [!IMPORTANT]
> A manutenção desta skill é vital para a sobrevivência do projeto durante a migração para a "coluna certa" das branches. Nunca ignore erros reportados por estas ferramentas.
