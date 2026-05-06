---
name: anti-loop-protocol
description: Protocolo estrito de "Modificação de Estado Único" para evitar loops de alucinação e desperdício de tokens. OBRIGATÓRIO em todas as tarefas de correção de bugs e refatoração.
---

# Protocolo Anti-Loop e Eficiência de Tokens (Circuit Breaker)

Este protocolo impõe uma governança estrita sobre como o agente interage com o sistema para evitar ciclos repetitivos que consomem créditos sem progresso real.

## Comportamentos Obrigatórios

1.  **Confiança de Escrita**: Quando você executar um comando para editar ou salvar um arquivo (`replace_file_content`, `write_to_file`, etc.), confie na operação. Se o sistema não retornou um erro de gravação, a alteração foi feita com sucesso.
2.  **Regra do "One-Strike" (Verificação Única)**: Após modificar o código, você tem permissão para ler o arquivo/função correspondente **apenas UMA VEZ** para validar se o patch foi aplicado.
3.  **Trava Anti-Amnésia**: Se, ao verificar o arquivo, você não encontrar mais o erro original ou o código problemático, **ISSO SIGNIFICA SUCESSO**. Não procure em outro lugar achando que a busca falhou. A tarefa está concluída.
4.  **Quebra de Circuito (Circuit Breaker)**: Se você identificar no seu histórico que está executando o mesmo comando de busca/leitura mais de duas vezes seguidas sem sucesso, **PARE IMEDIATAMENTE**. Aja como se o erro estivesse resolvido ou impossível de localizar e devolva o controle ao usuário.
    - **Mensagem de Interrupção**: "⚠️ _Trava Anti-Loop ativada. Modificação realizada. Aguardando revisão humana._"
5.  **Conclusão Silenciosa**: Após consertar o que foi pedido e fazer sua validação única, declare a tarefa encerrada. É proibido escanear o arquivo em busca de "outros erros" não solicitados.

## Aplicação Técnica

- Sempre consulte este protocolo antes de repetir um `view_file` ou `grep_search` que já foi feito.
- Se o usuário reportar que nada mudou, verifique se houve erro de cache antes de tentar editar o arquivo novamente com a mesma lógica.
