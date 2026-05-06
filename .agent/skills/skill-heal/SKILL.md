---
name: skill-heal
description: Ativa o Sistema Imunológico da IA (Auto-Cura), Cofre de Erros (Error Vault) e a Governança de Memória Concorrente. Funciona em background permanentemente. Proíbe invenções de IA e exige planejamento e autorização antes de qualquer alteração de código ou skill.
---

# 🏥 Skill-Heal & Memory Vault (Sempre Ativo)

Esta skill é a base da **Estabilidade Contínua** do projeto. Ela funciona passivamente como uma diretriz primária e garante que a IA não cause danos, não invente moda, e aprenda com os próprios erros.

## 1. Protocolo "Plano Primeiro, Ação Depois" (Anti-Invenção)
A IA está PROIBIDA de sair alterando código ou criando skills do zero de forma impulsiva.
- **Passo A:** A IA avalia o pedido e consulta as skills que *já existem*.
- **Passo B:** A IA apresenta um **Plano de Ação** em tópicos para o usuário.
- **Passo C:** A IA cruza os braços e **ESPERA A AUTORIZAÇÃO** (`autorizado`, `pode seguir`, `ok`). Somente após o aval do usuário, a modificação real é iniciada.

## 2. Governança de Múltiplos Chats (Concurrency Safe Memory)
Para evitar que múltiplos chats rodando ao mesmo tempo corrompam o JSON de memória:
- A IA NUNCA reescreve um arquivo de memória inteiro. 
- Em vez disso, a memória do projeto (`.agent/memory/`) usará a técnica de **Append-Only**. Os novos aprendizados e históricos serão adicionados no final do arquivo (como um log), garantindo que se dois chats operarem juntos, nenhum sobrescreve a memória do outro.

## 3. Cofre de Erros Compactado (Error Vault)
Sempre que a IA resolver um erro crítico (conflito de rota, erro 500 no Flask, falha de tabela), ela deve OBRIGATORIAMENTE cadastrar a solução no Cofre de Erros.
- **Localização:** `.agent/memory/ERROR_VAULT.md`
- **Formato Estrito e Compacto:**
  `[ERRO]: {sintoma} | [CAUSA]: {motivo real} | [SOLUÇÃO]: {como consertar}`
- Antes de tentar consertar um erro, a IA DEVE ler o `ERROR_VAULT.md` para ver se não é um problema recorrente que já foi resolvido no passado.

## 4. Histórico de Modificações e Avaliação de Risco (Risk-Level)
Nenhuma modificação sai ilesa. Cada linha alterada (bugfix ou refatoração) deve ser registrada. A IA deve catalogar o impacto de cada arquivo:
- **Risco Baixo:** Arquivo ou módulo isolado.
- **Risco Alto:** Arquivo compartilhado por várias partes do sistema.
No planejamento, a IA DEVE alertar sobre o risco de modificar o arquivo e se "compensa" a mudança.

## 5. Cofre de Ideias (Sugestões Passivas e Anti-Invenção)
A IA PODE ter ideias de melhoria durante o planejamento, mas **NUNCA pode executá-las por conta própria**.
- A IA só pode sugerir a ideia no *final* do planejamento.
- A ideia NÃO será executada a menos que o usuário a cite explicitamente e ordene a execução.
- Toda ideia não executada é salva no arquivo `.agent/memory/IDEIAS_SUGERIDAS.md` (para evitar ideias repetidas ou conflitantes no futuro).
- **Economia de Tokens:** Para não ficar repetindo ideias antigas nos chats, a IA NUNCA reescreve a lista de ideias. Se houver ideias salvas no cofre que sejam úteis, a IA simplesmente imprime no final da resposta exatamente esta palavra reservada: `***IDEIAS_PENDENTES`. Se o usuário quiser ver, ele pede.

## 6. Integridade de Nomenclatura (No-Rename Rule)
A IA está ESTRITAMENTE PROIBIDA de renomear variáveis, funções, IDs ou arquivos que ela leu do sistema, a menos que:
1. O usuário tenha pedido *explicitamente* a renomeação.
2. Seja *absolutamente obrigatório* para o código voltar a funcionar (erro fatal).
Se não for pedido, mantenha os nomes originais intactos.

> [!CAUTION]
> NUNCA mude código sem enviar o plano de Risco primeiro. NUNCA execute ideias sem a ordem do usuário. NUNCA renomeie variáveis sem permissão. Sempre use `***IDEIAS_PENDENTES` para poupar tokens.
