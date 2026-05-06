# 🤖 TRPROC_GOV v2: Manual Humano (Tradução do AI_CORE.min)

Este arquivo é a tradução legível das regras do `AI_CORE.min.txt`.
**Para a IA:** Sempre leia o `.min.txt` (custa ~100 tokens). Este `.human.md` custa ~1500 tokens e é só para humanos consultarem.

---

## Regras 1-8 (Originais)

| # | Código | Tradução |
|---|--------|----------|
| 1 | `PLN_1ST` | **Plano Primeiro.** Não aja nem faça análises profundas sem apresentar um plano e esperar autorização. |
| 2 | `RSK_EVAL` | Avaliação de Risco. Se risco Alto → não mexa no arquivo central. Isole. |
| 3 | `NO_REN` | Não Renomeie variáveis, funções ou arquivos sem ordem do usuário. |
| 4 | `DEAD_CD` | Não delete código morto antigo sem autorização expressa. |
| 5 | `ERR_VLT` | Cofre de Erros (Nexus). Registre por categoria. Delete erros que se tornaram impossíveis (purge). |
| 6 | `MEM_CONC` | Memória Concorrente. Só adicione no final do arquivo (append). Nunca sobrescreva. |
| 7 | `IDA_VLT` | Cofre de Ideias (Nexus). Salve com `[ID-XXX]`. Não execute até o usuário dizer "Aprovo ID-XXX". |
| 8 | `TKN_SVR` | Respostas curtas, só código necessário. Sem explicações longas. |

## Regras 9-19 (Novas v2)

| # | Código | Tradução |
|---|--------|----------|
| 9 | `TOOLKIT` | Use a pasta `ia-admin-toolkit` para testes e diagnósticos. |
| 10 | `OUT_MIN` | **Economia Extrema de Tokens.** A IA deve responder APENAS em Shorthand, a menos que você peça explicitamente uma explicação. |
| 11 | `RESP_FMT` | Formato restrito: `PLN:1.[arquivo]:ação. OK`. Proibido responder com textos longos nas operações padrão. |
| 12 | `CTX_MAP` | **Mapa de Contexto (Nexus).** Formato shorthand obrigatório para economizar tokens da IA. |
| 13 | `DUAL_SAVE` | **Salvamento Duplo.** Sempre salve em 2 formatos: `.human.md` (para você ler) e `.min.txt` (para a IA ler rápido). |
| 14 | `INIT` | **Auto-Inicialização.** Quando clonar o toolkit, rode `/smart-init` para criar pastas de memória, verificar skills e mesclar regras. |
| 15 | `LAZY_SKILL` | **Ativação Dinâmica.** Só leia a skill específica da tarefa que está fazendo. Nunca leia todas as skills de uma vez. |
| 16 | `RESUME` | **Restaurar Contexto.** Ao iniciar chat, leia o histórico (HISTORY.min.log) e o mapa (CONTEXT_MAP.min.txt) para lembrar onde parou. |
| 17 | `AUTO_EVOLVE` | **Auto-Melhoria.** Se achar um padrão valioso ou corrigir erro complexo, use `L.evoluir [skill]` para editar a skill e deixá-la mais inteligente. |
| 18 | `NO_GIT` | **Git Controlado.** A IA é proibida de usar `git add`, `commit` ou `push` sem autorização expressa do usuário. |
| 19 | `TRANSLATE_LAYER`| **Camada de Entendimento.** A IA ignora erros de digitação em português, mas a saída deve ser em Shorthand para poupar seus tokens. |
---

## Como usar no dia-a-dia

**Para iniciar um chat econômico (Claude Opus 4.6):**
> "Leia `./.agent/AI_CORE.min.txt` e siga estritamente."

**Para verificar o que foi feito:**
> Abra `AI_CORE.human.md` (este arquivo) e consulte a tabela.

**Para ver ideias pendentes que a IA guardou:**
> Abra `.agent/memory/IDEIAS_SUGERIDAS.md`
