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

## 4. Histórico de Modificações (Auto-Tracker)
Nenhuma modificação sai ilesa. Cada linha alterada (seja correção de erro ou refatoração) deve ser registrada.
- A IA descreve: "O que modificou", "O que causou o erro (se for bugfix)" e "Como estabilizou".
- Isso será salvo na memória principal do site.

> [!CAUTION]
> NUNCA crie uma skill do zero se ela já existe (apenas atualize-a). NUNCA mude código sem enviar o plano primeiro. NUNCA esqueça de documentar o erro no Vault.
