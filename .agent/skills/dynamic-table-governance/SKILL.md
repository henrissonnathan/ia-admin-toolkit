# Dynamic Table Governance Skill

## Overview

This skill governs the architecture of dynamic tables in the Formulario_referencial system. It enforces a "Single Engine" philosophy, where all dynamic table types (itens, dados externos, etc.) must share the same core rendering, persistence, and configuration logic.

## Core Principles

1. **ID Sovereignty**: All data must be bound to immutable numeric IDs (`coluna_db_id`). Slugs are for UI display and legacy mapping only.
2. **Engine Unification**: Do NOT create specialized editors or save handlers for new table types. Extend the `@ColumnTemplate` and `@TableConfigModule`.
3. **Cascading Persistence**: Data flows from `respostas_tabela` array in `salvar.php` into the relational schema.
4. **Idempotent Migrations**: All SQL changes to table structures must check for existing keys/columns before applying.

## Implementation Standards

### Frontend Configuration

- **Template**: Use `public_html/js/gerenciar_perguntas/column-template.js` for all column definitions.
- **Roles**: Semantic roles (e.g., `item_nome`, `quantidade`) must be mapped in the `papel_coluna` field.
- **Formulas**: Formulas are translated from Slugs to IDs upon saving to ensure stability if slugs change.

### Backend Persistence

- **saveHandlers**: Always use the unified `isTable` check in `public_html/js/gerenciar_perguntas/saveHandlers.js`.
- **salvar.php**: Ensure the question type is included in the `respostas_tabela` processing loop.

### Debugging & Diagnostics

- Use `console.log` for frontend debugging (avoid `error_log` with color codes).
- Use `TableUi.js` to inject debug buttons for real-time state inspection.

## Adding New Table Types

If a new table type is requested:

1. Add the type to the `isTable` arrays in `modalHandlers.js` and `saveHandlers.js`.
2. Update `column-template.js` if new UI fields are needed (e.g., masks, validation).
3. Ensure `salvar.php` recognizes the type for data persistence.
4. Update this skill to document the new type's role.
