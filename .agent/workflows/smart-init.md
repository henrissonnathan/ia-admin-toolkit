# /smart-init

**Descrição:** Protocolo de inicialização automática. Quando o toolkit é clonado ou baixado pela primeira vez, este workflow garante que tudo funcione sem erros e já configure a economia de tokens.

// turbo-all

## Fase 1: Criação da Estrutura de Memória
1. Verificar se `.agent/memory/` existe no projeto atual.
2. Se não existir, criar automaticamente:
   - `.agent/memory/ERROR_VAULT.md` (vazio, com cabeçalho)
   - `.agent/memory/IDEIAS_SUGERIDAS.md` (vazio, com cabeçalho)
   - `.agent/memory/HISTORY.min.log` (vazio)
   - `.agent/memory/CONTEXT_MAP.min.txt` (vazio, com template)
3. Garantir que `.agent/memory/` esteja no `.gitignore` do projeto.

## Fase 2: Verificação de Skills
1. Ler a lista de skills em `.agent/skills/`.
2. Para cada skill, verificar se possui **dois arquivos**:
   - `SKILL.md` (versão humana completa)
   - `SKILL.min.txt` (versão minificada para IA)
3. Se `SKILL.min.txt` não existir, a IA deve criá-lo automaticamente a partir do `SKILL.md`.

## Fase 3: Fusão de Regras (Rule Merge)
1. Ler `AI_CORE.min.txt` do toolkit.
2. Ler `GEMINI.md` ou regras do projeto atual.
3. Comparar: Se o projeto tiver regras específicas, **não sobrescrever**. Fazer merge, adicionando o que falta.

## Fase 4: Verificação Final (Health Check)
1. Confirmar que todos os arquivos de memória existem.
2. Confirmar que todas as skills possuem versão `.min.txt`.
3. Imprimir relatório em formato duplo:
   - **Humano:** `INIT_REPORT.human.md` (tabela legível)
   - **IA:** `INIT_REPORT.min.txt` (shorthand ultra-compacto)
4. Salvar os relatórios em `.agent/memory/`.
