# Health Check Report — 2026-05-06 10:53

| Status | Qtd |
|--------|-----|
| ✅ OK | 0 |
| ⚠️ Avisos | 5 |
| ❌ Erros | 3 |

## AI_CORE
- ❌ AI_CORE.min.txt não encontrado! As regras da IA não estão ativas.
  - Correção: Clone o toolkit novamente ou rode /update-toolkit.

## SKILLS
- ❌ A skill '(skills dir)' não possui arquivo SKILL.md (versão humana).
  - Correção: Esta skill está incompleta. Crie o SKILL.md com a documentação.

## TEMPLATES
- ⚠️ Template 'ERROR_VAULT.md' não encontrado em .agent/templates/.
  - Correção: Atualize o toolkit com /update-toolkit.
- ⚠️ Template 'IDEIAS_SUGERIDAS.md' não encontrado em .agent/templates/.
  - Correção: Atualize o toolkit com /update-toolkit.
- ⚠️ Template 'HISTORY.min.log' não encontrado em .agent/templates/.
  - Correção: Atualize o toolkit com /update-toolkit.
- ⚠️ Template 'CONTEXT_MAP.min.txt' não encontrado em .agent/templates/.
  - Correção: Atualize o toolkit com /update-toolkit.

## MEMORY
- ⚠️ A pasta de memória (.agent/memory/) não existe neste projeto.
  - Correção: Rode /smart-init para criar a estrutura de memória.
- ❌ A pasta .agent/memory/ não está no .gitignore. Dados privados podem vazar!
  - Correção: Adicione '.agent/memory/' ao .gitignore do projeto.
