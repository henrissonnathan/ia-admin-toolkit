# 🤖 TRPROC_GOV v2: Manual Humano (Tradução do AI_CORE.min)

Este arquivo é a tradução legível das regras do `AI_CORE.min.txt`.
**Para a IA:** Sempre leia o `.min.txt` (custa ~100 tokens). Este `.human.md` custa ~1500 tokens e é só para humanos consultarem.

---

## Regras 1-8 (Originais)

| # | Código | Tradução |
|---|--------|----------|
| 1 | `PLN_1ST` | Plano Primeiro. Não aja sem apresentar plano e esperar autorização. |
| 2 | `RSK_EVAL` | Avaliação de Risco. Se risco Alto → não mexa no arquivo central. Isole. |
| 3 | `NO_REN` | Não Renomeie variáveis, funções ou arquivos sem ordem do usuário. |
| 4 | `DEAD_CD` | Não delete código morto antigo sem autorização expressa. |
| 5 | `ERR_VLT` | Cofre de Erros. Registre `Erro|Causa|Solução`. Leia o cofre antes de consertar. |
| 6 | `MEM_CONC` | Memória Concorrente. Só adicione no final do arquivo (append). Nunca sobrescreva. |
| 7 | `IDA_VLT` | Cofre de Ideias. Não execute ideias. Salve no arquivo. Imprima `***IDEIAS_PENDENTES`. |
| 8 | `TKN_SVR` | Respostas curtas, só código necessário. Sem explicações longas. |

## Regras 9-14 (Novas v2)

| # | Código | Tradução |
|---|--------|----------|
| 9 | `TOOLKIT` | Use a pasta `ia-admin-toolkit` para testes e diagnósticos. |
| 10 | `OUT_MIN` | IA responde em formato curto (shorthand). Sem textos longos. |
| 11 | `RESP_FMT` | Formato de resposta: `PLN:1.[arquivo]:ação`. Diz "OK" quando acabou. |
| 12 | `CTX_MAP` | **Mapa de Contexto.** Leia `.agent/memory/CONTEXT_MAP.min.txt` antes de trabalhar. Atualize após modificar. |
| 13 | `DUAL_SAVE` | **Salvamento Duplo.** Sempre salve em 2 formatos: `.human.md` (para você ler) e `.min.txt` (para a IA ler rápido). |
| 14 | `INIT` | **Auto-Inicialização.** Quando clonar o toolkit, rode `/smart-init` para criar pastas de memória, verificar skills e mesclar regras. |

---

## Como usar no dia-a-dia

**Para iniciar um chat econômico (Claude Opus 4.6):**
> "Leia `C:\xampp\htdocs\ia-admin-toolkit\.agent\AI_CORE.min.txt` e siga estritamente."

**Para verificar o que foi feito:**
> Abra `AI_CORE.human.md` (este arquivo) e consulte a tabela.

**Para ver ideias pendentes que a IA guardou:**
> Abra `.agent/memory/IDEIAS_SUGERIDAS.md`
