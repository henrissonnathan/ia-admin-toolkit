# Análise Técnica: Mapeamentos Controller & Condições de Corrida

**Arquivo:** `public_html/js/gerenciar_mapeamentos/mapeamentos-controller.js`

## Problemas Identificados

1. **Condição de Corrida no Auto-Open:** O uso de `setTimeout(150)` para preencher campos no modal causava falhas intermitentes. Se o modal demorasse mais de 150ms para abrir, os seletores `#pergunta_id` e `#municipio_id` não eram encontrados, resultando em salvamentos com IDs vazios.
2. **Dependência de Seletores de Topo:** O `handleSave` dependia exclusivamente dos seletores da página principal, que podiam estar em estados inconsistentes durante a inicialização automática.

## Soluções Aplicadas

1. **Uso de Eventos do Bootstrap:** Substituído `setTimeout` pelo listener `shown.bs.modal`. Isso garante que o código de preenchimento só execute quando o modal estiver 100% pronto e seus elementos acessíveis no DOM.
2. **Robustez na Captura de Município:** Adicionados seletores globais (`window.AppConfig`, `#municipio-selector`) para garantir que o ID do município seja capturado mesmo em contextos diferentes (Admin vs Cliente).

## Verificação Sugerida

- Abrir a URL com `auto_open=true&pergunta_id=X&municipio_id=Y`.
- Verificar no console se o log `[TableEvents] Abrindo mapeamento...` contém os valores corretos.
- Tentar salvar um novo mapeamento e observar se o erro de "identificadores ausentes" persiste.
