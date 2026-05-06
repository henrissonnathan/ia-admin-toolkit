# Análise Técnica: `public_html/js/formulario/items/table/core/TableEvents.js`

## Descrição

Gerencia os eventos de interação das tabelas dinâmicas, incluindo o clique no botão de mapeamento.

## Mudanças Realizadas (Prevenção de Loop)

- **Correção da Captura de `municipio_id`**: O método `_setupActionButtons` foi modificado para tentar capturar o `municipio_id` de múltiplas fontes:
  1. Input `#municipio_id`
  2. Input `.municipio_id` (classe)
  3. Estado global `window.formularioState.municipio_id`
- **Motivo**: O botão inferior não estava enviando o ID do município, resultando em erro de "identificadores ausentes" no controller de mapeamento.

## Pontos de Atenção

- Se o `municipio_id` não for encontrado em nenhuma dessas fontes, o mapeamento falhará. É necessário garantir que o formulário principal carregue este ID.
