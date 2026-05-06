# /optimize-tokens

**Descrição:** Ativa o Modo Econômico Avançado (Baseado nas melhores práticas globais de Engenharia de Contexto para Cursor/GitHub Copilot). Reduz drasticamente o gasto de tokens e a ocorrência de alucinações da IA.

## Workflow de Execução (O que a IA deve fazer)

1. **Ativação do Modo Snippet Estrito (Token Saver):**
   - A IA está PROIBIDA de reescrever funções que não foram modificadas.
   - Retornar APENAS o bloco de código exato que mudou (snippet).
   - Nenhuma explicação técnica longa a menos que o usuário inclua a palavra "Explique".

2. **Fechamento de Contexto Passivo (Regra do IDE):**
   - A IA deve lembrar ao usuário: *"Por favor, feche as abas (arquivos) do seu editor que não estamos usando agora. O sistema lê as abas abertas e gasta seus tokens à toa!"*

3. **Arquitetura de Conversas Curtas:**
   - A IA deve avaliar se a conversa atual está muito longa (mais de 10-15 interações). Se estiver, deve gerar um `TECHNICAL_MEMORY.json` compacto através da skill `trproc-context-master` e instruir o usuário a **abrir um novo chat limpo**, fornecendo um resumo de 3 linhas para iniciar a próxima conversa.

4. **Diretiva de Erros Específicos:**
   - Se houver erro no console, a IA deve orientar o usuário a mandar *apenas* a linha do erro, e nunca o log inteiro.

5. **Validação e Saída:**
   - A IA deve responder estritamente com: "🚀 **Modo Token Saver PRO Ativado! Respostas ultracurtas e estritas. Feche as abas inúteis no seu VSCode para economizarmos ainda mais.**"

// turbo-all
