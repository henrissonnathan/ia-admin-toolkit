---
name: legacy-data-mapper
description: Gerencia a ponte de dados entre estruturas legadas (Slugs) e a nova arquitetura de IDs Estáveis. Essencial para importação de Excel, preenchimento de formulários antigos e transições de banco de dados. Integra-se ao fluxo modular na camada p1.
---

# Legacy Data Mapper: Protocolo de Tradução de Estado

Esta skill orienta a conversão de payloads "sujos" ou legados em estados "limpos" e vinculados a IDs, garantindo que o sistema SaaS suporte dados históricos sem perda de integridade.

## 1. O Papel do Mapeador na Camada p1 (Coordenação)

O mapeamento de dados não deve ocorrer na visualização (p0) nem na persistência pura (p3). Ele é uma tarefa de **Coordenação de Estado (p1)**.

- **Entrada**: Payload JSON bruto vindo do `p0` (pode conter Slugs/Chaves legadas).
- **Processo**: O `p1` consulta o `LegacyDataMapper` (via API ou objeto carregado).
- **Saída**: Dados "Normalizados" onde cada valor está associado ao ID numérico correto da coluna.

## 2. Princípios de Tradução Estrita

### **Dicionário de Tradução (Reverse Mapping)**

Todo mapeamento resolvido deve seguir o contrato: `{"coluna_origem": "id_estavel_destino"}`.

- **Exemplo**: `{"VALOR_UNIT": "328", "QTD_PEDIDO": "329"}`.

### **Validadores "Anti-Corrupção"**

Ao realizar a tradução, o sistema **DEVE**:

1. Verificar se o ID de destino ainda é válido na pergunta atual.
2. Preservar o valor original se a tradução falhar (para auditoria), mas impedi-lo de ser renderizado em campos errados.

## 3. Fluxo de Hidratação Smart (Frontend Integration)

O `DataHydrator.js` deve ser instruído a:

1. Detectar o "Cheiro de Legado" (presença de chaves não numéricas no JSON de respostas).
2. Chamar o endpoint `obter_mapeamento_para_importacao.php` passando o `pergunta_id`.
3. Injetar o dicionário no `LegacyTableAdapter.js`.
4. Traduzir o JSON **ANTES** da tabela renderizar a primeira linha.

## 4. Gerenciamento de Conflitos (Multi-Tenant Zero Trust)

- **Soberania do Município**: Mapeamentos podem ser globais (`municipio_id IS NULL`) ou específicos. O `p1` deve sempre priorizar o mapeamento específico do cliente.
- **Audit Log**: Qualquer tradução realizada durante um salvamento deve ser registrada silenciosamente no log de segurança (`p5`) para rastreamento de migração silenciosa.

## 5. Gatilhos de Ação Prioritários

Use esta skill sempre que:

- O usuário relatar que "campos de tabelas antigas estão voltando vazios".
- Houver necessidade de importar dados de arquivos CSV/Excel onde os nomes das colunas não coincidem com os IDs.
- For necessário migrar uma pergunta do tipo `input` (estático) para `tabela` (dinâmico).

## 7. Escopo de Operação: Leitura para Transformação

A Skill `legacy-data-mapper` é uma ferramenta de **Transição e Hidratação**.

- **USAR PARA**: Preencher tabelas vazias no modo edição quando o usuário possui dados históricos em slugs.
- **PROIBIDO USAR PARA**: Qualquer operação de `SAVE`, `UPDATE` ou `INSERT` de novos dados.
- **Lógica de Automação**: Se `MODERN_DATA` for nulo, acionar busca de `LEGACY_DATA`. Após o primeiro SAVE do usuário, os dados devem estar migrados no JSON moderno e o mapper não deve ser mais a fonte primária.
