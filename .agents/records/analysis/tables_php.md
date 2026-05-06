# Análise Técnica: `includes/formulario_partes/perguntas/tables.php`

## Descrição

Responsável por gerar o HTML das tabelas dinâmicas no formulário.

## Mudanças Realizadas (Prevenção de Loop)

- **Remoção do Botão Superior**: O botão "GERENCIAR MAPEAMENTOS" que ficava logo abaixo do título da tabela foi removido para evitar duplicidade com o botão da dropzone.
- **Motivo**: O usuário relatou que o botão aparecia em cima e embaixo, causando confusão. O botão superior foi removido em favor do inferior que está integrado ao fluxo de upload/mapeamento.

## Pontos de Atenção

- O modal de mapeamento (`modalMapeamentoImportacao_...`) ainda é gerado neste arquivo e é necessário para o funcionamento do botão inferior.
