---
name: dynamic-form-orchestrator
description: Orquestra o ciclo de vida completo de formulários complexos no Formulario_referencial. Integra Tabelas Dinâmicas, Regras de Visibilidade e Módulos de Responsáveis (Gestores/Unidades). Use esta skill para garantir que a geração de campos dinâmicos em cascata e o salvamento multi-etapas funcionem sem perda de dados ou conflitos de IDs.
---

# Maestro do Formulário Dinâmico: Integração Máxima

Esta skill consolida a arquitetura "Zero Dor de Cabeça" para o formulário completo, focando na integração entre diferentes módulos e na geração de campos dinâmicos complexos.

## 1. Padrão de Unidades e Responsáveis (Gestão de Cards)

O sistema utiliza um padrão avançado de **Múltipla Seleção com Geração de Dependências**.

### Fluxo de Unidades Requisitantes

1.  **Gatilho**: O usuário seleciona 1 ou mais itens em uma lista de Unidades (Checkboxes ou Multiselect).
2.  **Expansão Dinâmica**: Para CADA unidade selecionada, o sistema deve gerar um bloco (Card) contendo sub-perguntas (ex: Matrícula e Nome do Gestor).
3.  **Identificação Estrita**: Os campos gerados devem conter o ID da unidade no nome (ex: `gestor_nome_{unidade_id}`) para garantir que o backend saiba a quem pertence aquele dado.
4.  **Auto-Preenchimento**: Integrar o módulo de `autocomplete` em cada novo campo de responsável criado dinamicamente.

## 2. Persistência Integrada e Edição

### Salvamento (UPSERT Multi-Módulo)

- **Tabelas**: Salvas via payload JSON traduzido para IDs estáveis.
- **Respostas**: Salvas via Sigla/CampoID.
- **Responsáveis**: Salvos através de tabelas relacionais auxiliares para suportar a multiplicidade (N responsáveis para 1 formulário).

### Carregamento (Hidratação)

Ao abrir um formulário para edição:

- **Prioridade 1**: Carregar estrutura de colunas do banco.
- **Prioridade 2**: Buscar dados das perguntas simples.
- **Prioridade 3**: Disparar buscas assíncronas para módulos complexos (Gestores/Fiscais) para preencher os cards dinâmicos.

## 3. Navegação Multi-Páginas e Visibilidade

- O orquestrador deve garantir que regras de visibilidade funcionem mesmo entre páginas diferentes.
- **Regra de Ouro**: Se uma página inteira for ocultada, os campos obrigatórios dentro dela não devem impedir o salvamento do formulário.

## 4. UX e Visualização Premium

- **Feedback Visual**: Usar estados de carregamento (`loader`) enquanto as unidades e gestores são buscados do banco.
- **Validação Antecipada**: Bloquear o salvamento se uma Unidade foi selecionada mas os campos do seu respectivo Gestor ficaram vazios.

## 5. Vínculo de Estrutura Multi-Município

O sistema permite que um município utilize a estrutura de colunas (template) de outro município ou de um padrão global.

- **Importação de Estrutura**: Ao carregar a tabela, se o `municipio_id` atual não possuir colunas definidas, o orquestrador deve buscar no `municipio_id` de origem (template).
- **Consistência de Mapeamento**: Se a estrutura for importada, o `LegacyDataMapper` deve ser acionado para garantir que os dados salvos anteriormente no município destino se encaixem perfeitamente nos IDs da nova estrutura importada.

## 6. Protocolo de Hidratação Inteligente (Soberania)

O Orquestrador deve coordenar o `DataHydrator` seguindo a regra de soberania:

1.  **Check Modern**: Verificar `respostas_dinamicas_salvas`. Se houver dados no formato JSON moderno (IDs), ignorar legado.
2.  **Fallback Legacy**: Se os dados modernos estiverem vazios (`[]` ou `null`), o Orquestrador deve invocar o `LegacyDataMapper` para tentar traduzir chaves antigas.
3.  **Conversão de Estado**: Após a primeira interação de salvamento, o Orquestrador garante que o payload enviado para o backend p0 esteja 100% no formato moderno, "congelando" a migração.

## Checklist de Implementação (Novo Campo Complexo)

- [ ] Criar o Trigger de evento (ex: `on('change')`) na lista mestre.
- [ ] Implementar a função de `renderCards()` que limpa e reconstrói o container de dependências.
- [ ] Garantir que o `name` e `id` dos inputs gerados incluam o ID da entidade pai.
- [ ] Adicionar a chamada de API no modo Edição para buscar os dados salvos previamente.
