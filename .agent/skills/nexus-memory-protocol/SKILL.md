---
name: nexus-memory-protocol
description: "Protocolo central de gerenciamento de memória da IA. Controla o Cofre de Erros (categorizado e com autolimpeza), o Cofre de Ideias (com IDs de aprovação) e o Mapa de Contexto (em formato minificado/shorthand)."
---

# 🧠 Protocolo Nexus (Nexus-Memory Protocol)

O **Protocolo Nexus** é o sistema que gerencia como a IA lembra, arquiva e esquece informações. Para facilitar nossa comunicação, quando o humano disser *"Aplica o Protocolo Nexus"* ou *"Atualiza o Nexus"*, ele está se referindo a este ecossistema de memórias.

Este protocolo divide a memória em três pilares funcionais e otimizados:

## 1. Cofre de Erros Categorizado e Autolimpante (`ERROR_VAULT.md`)
O cofre de erros não é mais uma lista bagunçada.
* **Categorização Obrigatória:** Todo erro deve ser salvo em uma categoria específica (ex: `## [DB] Banco de Dados`, `## [UI] Interface`, `## [SEC] Segurança`).
* **Regra de Autolimpeza (Purge):** Se o sistema mudar de forma que um erro antigo se torne matematicamente ou logicamente impossível de acontecer (ex: a tabela foi deletada, ou o framework mudou), a IA tem a obrigação de **apagar/arquivar** aquele erro do cofre para não poluir a memória.

## 2. Sistema de Ideias Baseado em IDs (`IDEIAS_SUGERIDAS.md`)
A IA é proibida de implementar ideias otimizadas durante uma tarefa sem autorização.
* **Tagueamento:** Quando a IA tiver uma ideia, ela vai salvar no cofre gerando um ID único.
  * *Exemplo:* `[ID-001] Trocar o loop foreach por bulk INSERT para salvar 300ms.`
* **Aprovação Modificada:** O usuário pode a qualquer momento dizer: *"Me mostre as ideias"* e depois *"Aprovo a [ID-001], mas em vez de aplicar em todos, aplique só na tabela X"*. A IA vai resgatar o contexto do ID-001 e aplicar com a restrição.

## 3. Mapa de Contexto Shorthand (`CONTEXT_MAP.min.txt`)
O Mapa de Contexto nunca deve ser escrito em texto longo (linguagem humana).
* **Formatação Restrita:** Deve ser escrito exclusivamente no formato "minificado" (Shorthand / Pseudo-código) que a IA usa no AI_CORE.min.txt.
* **Objetivo:** Otimização máxima. Quando a IA inicia um novo chat e carrega o mapa, ela gasta o mínimo de tokens possível para entender a arquitetura do projeto atual.

---

## ⌨️ Comandos Rápidos (Shortcuts)
Para economizar tempo e padronizar as ações, você pode usar os seguintes atalhos diretamente no chat:
* **`L.cmd`** ➔ Lista todos os comandos rápidos do Toolkit para você não esquecer.
* **`L.lista`** ➔ A IA lê o `IDEIAS_SUGERIDAS.md` e lista as ideias pendentes com seus IDs.
* **`L.aprovar [ID-XXX]`** ➔ A IA executa imediatamente a ideia solicitada.
* **`L.limpo`** ➔ A IA faz uma "faxina" no `ERROR_VAULT.md`, apagando erros que já não fazem mais sentido.
* **`L.mapa`** ➔ A IA relê a estrutura e atualiza o `CONTEXT_MAP.min.txt`.
* **`L.evoluir [skill]`** ➔ A IA analisa o que aprendeu de novo e atualiza o `SKILL.min.txt` da skill para ela ficar mais inteligente.

---

### ⚠️ Regras para a IA
1. Ao receber `L.limpo`, avalie se os erros do cofre ainda fazem sentido e delete os irrelevantes.
2. Toda ideia no `IDEIAS_SUGERIDAS` DEVE ter um prefixo `[ID-XXX]`.
3. Ao receber `L.lista`, liste todas as ideias pendentes com seus IDs.
4. O `CONTEXT_MAP.min.txt` não pode conter parágrafos, apenas estrutura de dados pura (ativado por `L.mapa`).
