# Tarefa: Resolução de Mapeamento e Importação de Tabelas Dinâmicas

- **ID**: task_resolve_table_mapping_import_v1
- **Status**: Em Progresso
- **Objetivo**:
  1. Remover o botão 'Gerenciar Mapeamento' superior em `tables.php`.
  2. Corrigir o botão inferior para garantir que ele capture o ID do município.
  3. Validar a seleção de município/tabela antes de permitir o mapeamento.
  4. Investigar falhas na lógica de importação (dados mapeados).

## Arquivos Envolvidos

- `includes/formulario_partes/perguntas/tables.php`
- `public_html/js/formulario/items/table/core/TableEvents.js`
- `public_html/js/formulario/items/table/core/TableUi.js`

## Progresso

- [x] Remoção do botão duplicado (Confirmado pelo usuário)
- [x] Correção da captura do ID do município (Confirmado pelo usuário)
- [x] Investigação da lógica de importação (Confirmado pelo usuário)
- [x] Implementar trava para impedir abertura do mapeamento sem Município e Tabela selecionados (Concluído)
- [x] Validar obrigatoriedade antes de abrir `gerenciar_mapeamentos.php` (Concluído)
