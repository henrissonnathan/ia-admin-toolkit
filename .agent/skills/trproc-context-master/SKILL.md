---
name: trproc-context-master
description: Protocolo de manutenção de Memória Técnica e Contexto do TRPROC. Garante que a IA sempre tenha acesso a um resumo atualizado do projeto, economizando tokens e evitando alucinações.
---

# Protocolo TRPROC Context Master

Este protocolo é **OBRIGATÓRIO** para manter a sanidade técnica do projeto e garantir que qualquer agente (IA) saiba exatamente o que foi feito e onde encontrar cada funcionalidade.

## Ferramentas de Contexto

### 1. Mapa Técnico (`TECHNICAL_MAP.json`)
Sempre que houver mudanças estruturais (novas rotas, novos controllers, funções JS críticas), execute o gerador de contexto.
- **Comando**: `py .agents/skills/trproc-admin-toolkit/scripts/context_generator.py`
- **Objetivo**: Atualizar o índice de rotas, funções e docstrings para consulta rápida.

### 2. Log de Desenvolvimento (`DEVELOPMENT_LOG.md`)
Mantenha um log contínuo de decisões arquiteturais na raiz do projeto.
- **Regra**: Todo `commit` ou mudança significativa deve ser registrado com:
  - **Data**: ISO 8601
  - **O Que**: Resumo da mudança
  - **Por Que**: Motivação técnica (ex: "Corrigir regras órfãs para evitar erro no Motor Monstro")
  - **Arquivos**: Lista de arquivos afetados.

## Fluxo de "Economia de Tokens"

Antes de iniciar qualquer análise profunda em arquivos grandes (ex: `formulario.js` com 4k+ linhas):
1.  **Consulte o `TECHNICAL_MAP.json`** para localizar a função alvo.
2.  **Leia apenas o bloco de código** necessário usando `view_file` com `StartLine` e `EndLine`.
3.  **Atualize o mapa** após a modificação.

## Testes Dinâmicos (Fuzzing)

Use o `smart_fuzzer.py` para validar se as novas entradas de dados suportam:
- Strings de alta densidade (limites de caracteres).
- Caracteres especiais (blindagem contra injeção).
- Valores nulos/vazios.

> [!IMPORTANT]
> A falha em atualizar o `TECHNICAL_MAP.json` após mudanças estruturais é considerada um erro de governança grave.
