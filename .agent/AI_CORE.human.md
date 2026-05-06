# 🤖 TRPROC_GOV: Manual Humano (Tradução do AI_CORE.min)

Este arquivo é a tradução legível para humanos das regras ofuscadas do `AI_CORE.min.txt`. 
As regras no arquivo `.min.txt` custam cerca de 80 tokens, enquanto esta explicação custaria quase 1000 tokens para a IA ler a cada interação. Para economizar dinheiro na API do Claude/OpenAI, sempre mande a IA ler o `.min.txt`.

## O que significam os códigos no `AI_CORE.min.txt`?

1. **`1.PLN_1ST: !ACT. req(PLN). wait(USR_AUTH).`**
   - **Tradução:** "Regra 1: Plano Primeiro. Não aja (!ACT). Requeira um plano. Espere a autorização do usuário." A IA não faz nada sem você mandar.

2. **`2.RSK_EVAL: if(RSK==HIGH)->!mod_core->iso_mod.`**
   - **Tradução:** "Regra 2: Avaliação de Risco. Se o risco for Alto, não modifique o código central. Isole a modificação em um novo arquivo/lógica."

3. **`3.NO_REN: !ren(var|func|file) unless USR_CMD|FATAL.`**
   - **Tradução:** "Regra 3: Não Renomeie. Não altere nomes de variáveis, funções ou arquivos a menos que o usuário mande ou seja um erro fatal."

4. **`4.DEAD_CD: !rm(dead_code) unless USR_AUTH.`**
   - **Tradução:** "Regra 4: Código Morto. Não remova códigos velhos ou inúteis sem autorização expressa do usuário."

5. **`5.ERR_VLT: log_err->.agent/memory/ERROR_VAULT.md(E|C|S). rd(VAULT) b4 fix.`**
   - **Tradução:** "Regra 5: Cofre de Erros. Se resolver um erro, grave no formato Erro|Causa|Solução. A IA deve sempre ler o cofre antes de tentar consertar algo."

6. **`6.MEM_CONC: append_only(.agent/memory/HISTORY.min.log).`**
   - **Tradução:** "Regra 6: Concorrência de Memória. Apenas adicione linhas no final do arquivo de histórico, nunca sobrescreva, para evitar que chats diferentes se destruam."

7. **`7.IDA_VLT: !exe_idea. save->IDEIAS_SUGERIDAS.md. print="***IDEIAS_PENDENTES".`**
   - **Tradução:** "Regra 7: Cofre de Ideias. Não execute ideias próprias. Salve no arquivo de ideias. E apenas imprima `***IDEIAS_PENDENTES` para o usuário, poupando tokens de explicação."

8. **`8.TKN_SVR: short_ans. snippet_only. !expl unless req.`**
   - **Tradução:** "Regra 8: Token Saver. Respostas curtas, apenas o código necessário. Sem explicações longas a menos que o usuário peça."

9. **`9.TOOLKIT: use(C:\xampp\htdocs\ia-admin-toolkit) 4 tests.`**
   - **Tradução:** "Regra 9: Toolkit. Todos os diagnósticos de peso devem ser feitos rodando os scripts desta pasta isolada."
