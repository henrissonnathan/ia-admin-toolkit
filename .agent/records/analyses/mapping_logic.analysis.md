# Análise Técnica: Módulos de Mapeamento e Tabela Dinâmica

## Arquivo: includes/formulario_partes/perguntas/tables.php

- **Função**: `render_tabela_itens_dinamica`.
- **Problema Identificado**: Injeta um botão de configuração de mapeamento via `onclick` direto no PHP (linhas 230-234) dentro de um `alert-warning` quando a tabela não tem colunas. Isso gera o botão superior que o usuário quer remover.
- **Lógica de Dados**: Injeta rascunhos de itens e grupos via JSON.

## Arquivo: public_html/js/formulario/items/table/core/TableUi.js

- **Função**: `renderDropzone`.
- **Problema Identificado**: Injeta dinamicamente o segundo botão "GERENCIAR MAPEAMENTOS" (linha 123) no rodapé da tabela.
- **Captura de Dados**: Tenta obter `municipioId` do `window.formularioState` ou `dataset.municipioId` no momento da renderização (linhas 103-106). Se o estado não estiver pronto, a URL fica incompleta.

## Arquivo: public_html/js/formulario/items/table/core/TableEvents.js

- **Função**: `_setupActionButtons` (EventListener delegado).
- **Problema Identificado**: O listener para `.btn-gerenciar-mapeamento` (linhas 63-89) tenta recapturar o `municipio_id` (`m`) usando seletores globais como `input[name="municipio_id_alvo"]`.
- **Falha**: Se o campo não existir ou o valor for `null`, ele exibe um erro do `Swal`. O botão inferior parece falhar nessa captura ou o seletor está retornando vazio no momento do clique.

## Arquivo: mapeamentos-controller.js (Inferido)

- **Erro**: `Falha ao salvar: identificadores ausentes. {mId: null, pId: '', isAdmin: true}`.
- **Causa**: A URL gerada para abrir o gerenciador de mapeamentos provavelmente está indo com `pergunta_id=` (vazio) ou `municipio_id=null`.

## Arquivo: user_style.js (Inferido)

- **Erro**: `TypeError: Cannot read properties of null (reading 'querySelector')`.
- **Causa**: Algum script de extensão ou tema customizado tentando acessar o DOM antes do carregamento completo ou em elementos que não existem na página de mapeamento.
