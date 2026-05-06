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

## 4. Avaliação de Risco (Risk-Level) e Isolamento
A avaliação de risco serve para a IA calcular o **nível de cuidado** antes de tocar no código:
- **Risco Baixo:** Arquivo isolado.
- **Risco Alto:** Se a modificação exigir alterar outras partes do sistema juntas para não quebrar.
**Regra de Ouro do Risco Alto:** Se a IA perceber que o risco é Alto, ela NÃO DEVE modificar o arquivo central diretamente. Em vez disso, ela deve propor fazer a alteração de forma **separada** (ex: criando um arquivo novo que herda ou consome o antigo, ou um módulo isolado) para proteger a arquitetura original.

## 5. Cofre de Ideias (Sugestões Passivas e Anti-Invenção)
A IA PODE ter ideias de melhoria durante o planejamento, mas **NUNCA pode executá-las por conta própria**.
- Toda ideia não executada é salva no arquivo `.agent/memory/IDEIAS_SUGERIDAS.md`.
- **Economia de Tokens:** A IA simplesmente imprime no final da resposta a palavra reservada: `***IDEIAS_PENDENTES`. 

## 6. Integridade de Nomenclatura (No-Rename Rule)
A IA está ESTRITAMENTE PROIBIDA de renomear variáveis, funções ou IDs que ela leu do sistema, a menos que o usuário peça explicitamente ou seja obrigatório para resolver um erro fatal.

## 7. Proteção de Código Morto (Dead-Code Rule)
A IA deve evitar escrever código morto (inútil). Porém, **É PROIBIDO APAGAR CÓDIGO MORTO ANTIGO**. A exclusão de qualquer código legado ou morto só pode ser feita se a IA sugerir no planejamento e o Admin **autorizar expressamente** a exclusão.

> [!CAUTION]
> NUNCA mude código sem enviar o plano de Risco primeiro. NUNCA execute ideias sem a ordem do usuário. NUNCA renomeie variáveis sem permissão. Sempre use `***IDEIAS_PENDENTES` para poupar tokens.
