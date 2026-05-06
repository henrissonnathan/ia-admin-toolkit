---
name: dynamic-question-logic
description: Gerencia a lógica de negócio de perguntas dinâmicas, incluindo motor de regras (esconder/mostrar), filtros de listagem por banco de dados e comportamento inteligente de campos e colunas. Use esta skill para configurar interações complexas no formulário sem quebrar a integridade dos dados.
---

# Mestre de Lógica de Perguntas Dinâmicas

Esta skill foca em tornar o formulário "vivo", automatizando a visibilidade e o conteúdo dos campos com base nas respostas e dados do banco.

## 1. Motor de Regras e Visibilidade

- **Esconder/Mostrar Inteligente**: Permite esconder perguntas ou colunas de tabelas dinâmicas.
- **Resiliência de Identidade**: As regras devem ser amarradas ao ID estável da pergunta ou coluna. Se o Slug mudar, a regra deve continuar funcionando.
- **Tipos Flexíveis**: Suporta a mudança de tipo de pergunta (ex: de `texto` para `seleção`) sem perder as regras de visibilidade vinculadas.

## 2. Listagens e Filtros de Banco de Dados

- **Busca via DB**: Configuração de campos que trazem opções diretamente de queries SQL ou APIs.
- **Filtros Dependentes (Cascata)**:
  - Exemplo: Selecionar "Estado" e a lista de "Cidades" filtrar automaticamente.
  - **Auto-Seleção**: Se sobrar apenas 1 opção após o filtro, o sistema deve selecioná-la e disparar as regras seguintes.
- **Sugestões Ativas**: Campos de texto que sugerem respostas do banco mas permitem digitação livre.

## 3. Lógica Especializada para Tabelas

- **Esconder Colunas via Regra**: Colunas específicas da tabela dinâmica somem se uma condição externa (ou interna da linha) for atendida.
- **Alertas e Bloqueios**: Disparar avisos (`Swal.fire`) se valores na tabela excederem limites definidos ou não seguirem normativas.

## 4. Comportamento do Gerenciador

Ao utilizar o Gerenciador de Perguntas:

- **Prioridade de Simplicidade**: Facilitar a criação de regras sem precisar escrever código, apenas selecionando "Se [Pergunta A] = [Valor X], então [Esconder Pergunta B]".
- **Preservação**: Nunca apagar as regras ao editar uma pergunta, a menos que o usuário solicite explicitamente.

## Resolução de Problemas

- **Loop de Regras**: Evitar que a Pergunta A esconda a B, e a B esconda a A.
- **Validação de Ocultos**: Garantir que campos escondidos por regra não bloqueiem o envio do formulário por serem "obrigatórios".
