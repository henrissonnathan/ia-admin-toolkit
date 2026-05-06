# Mapa Técnico do Sistema de Tabelas Dinâmicas

**Skill Ativada:** PROTOCOLO AUTO-DOC & DB-MAX
**Localização:** `.agents/records/analyses/mapa_tecnico_tabelas_dinamicas.md`

Este documento atua como o "GPS Técnico" do sistema de Tabelas Dinâmicas (Frontend e Backend), mapeando o fluxo de dados desde a interação do usuário na interface até a persistência no banco de dados. Este guia foi gerado para otimizar futuras integrações e refatorações, reduzindo o consumo de tokens na análise do sistema.

## 1. Dicionário de Atributos HTML (Frontend)

Os componentes de tabela utilizam diversos `data-attributes` para controle de estado, referenciamento e ligação com os registros do banco de dados (Soberania do Backend - IDs Estáveis).

- **`data-pergunta-id`**: Utilizado no container principal (`.dynamic-table-container`) para associar a tabela a uma pergunta específica do formulário e carregar a configuração correta.
- **`data-col-key`**: Presente nos elementos `<th>` do cabeçalho da tabela, guarda o ID numérico exato da coluna no banco de dados. Fundamental para o motor não perder a referência das colunas.
- **`data-slug` / `data-slug-coluna`**: Usado como identificador legível/legado das colunas (Ex: `unid`, `qtd`, `valor_unitario`). Internamente, o `DynamicItemsTableController` traduz esses slugs para os `coluna_id` reais (IDs Estáveis).
- **`data-papel` / `data-papel-coluna`**: Define o comportamento de cálculo ou formatação daquela coluna específica (Ex: `grupo`, `moeda`, `quantidade`, `total`). Usado pelo `TableCalculator` e pelo `TableGroupingHandler`.
- **`name="array[]"`**: Os inputs de cada linha utilizam notação de array (ex: `name="unid[]"`, `name="valor_unitario[]"`) para compatibilidade com o parse serializado ou montagem do JSON.

## 2. Fluxo de Dados (Da UI ao PDO)

O ciclo de vida da informação numa Tabela Dinâmica segue uma ordem estrita de renderização, captura, empacotamento e persistência:

1.  **Inicialização (Frontend):** O `DynamicItemsTableController.js` assume o contêiner e orquestra a tabela. Ele carrega as colunas do DB (`_loadColumnsFromDatabase`), instancia o `TableDataManager` e renderiza o HTML (`TableUi.js`).
2.  **Interação do Usuário (`addLinha`):** O usuário clica em "Adicionar Linha". O `TableEvents.js` intercepta o clique, chama `this.controller.addRow()`, que delega para o `TableDataManager.js` injetar a linha em lotes (`_renderRowsBatch`) ou singularmente, disparando regras via `TableRuleHandler`.
3.  **Captura (`prepararValoresParaSalvar` / `getTableDataForSubmission.js`):**
    - As regras ou ações de salvamento acionam rotinas que varrem a tabela DOM.
    - O script extrai os dados dos inputs/textareas, removendo símbolos de moeda (`R$`), espaços e formatando os números para um padrão float (ex: `1.000,50` vira `1000.50`).
    - **Filtro Inteligente:** Linhas vazias são expurgadas aqui. Apenas as que contêm descrições não-vazias ou valores de `quantidade > 0` e `valor_unitario > 0` são incluídas.
4.  **Empacotamento (`handleFormSubmit.js`):** Durante o envio do formulário, o JS pega o JSON filtrado das linhas, aplica o `JSON.stringify()`, insere na variável global/POST sob a chave `tableData` (ou equivalente no array `pergunta_dinamica`) e cria o payload do `FormData`.
5.  **Envio (Fetch):** Dispara a requisição assíncrona POST para o endpoint `acoes/formulario/persistencia/salvar.php`.
6.  **Persistência Backend (`salvar.php`):**
    - O arquivo itera por todas as perguntas da configuração (`$dbgPerguntas`).
    - Ao identificar `$isTabelaDinamica` (ex: `tabela_itens_dinamica`), puxa os dados enviados (via `$_POST['pergunta_dinamica'][$perguntaId]` ou correlato).
    - **Filtro de Segurança Backend:** Executa um `array_filter` adicional no PHP garantindo que as linhas que contêm apenas espaços (`trim($val) === ''`) não sejam processadas.
    - **Salvamento Otimizado (JSON):** Realiza a persistência empacotando as linhas válidas novamente em JSON (`json_encode($itensValidos)`) e rodando um único `INSERT/UPDATE` na tabela `respostas_dinamicas` (`$stmtResposta->execute`), abandonando a antiga tabela relacional (`respostas_tabela_dinamica`) para ganho de performance.

## 3. Identificação de Riscos (Bug Hunting e Cuidados a ter)

Para evitar falhas na arquitetura modular P0-P5 e garantir a soberania de dados, observe os seguintes riscos e pontos de atenção:

- **Sanitização Anti-XSS (OBRIGATÓRIA):**
  - Desde a refatoração de 23/04/2026, o `salvar.php` aplica `htmlspecialchars(strip_tags($value), ENT_QUOTES, 'UTF-8')` em todas as células da tabela dinâmica antes de persistir no banco.
  - O `ia-data-collector.js` (Frontend) faz o decode inverso nas linhas 74-78: `txt.innerHTML = val; val = txt.value` para que a IA receba dados limpos sem &quot; ou &amp;.
  - **Cuidado:** Não aplique htmlspecialchars duas vezes (backend + frontend) ou os dados ficarão duplamente encodeados (&amp;amp;).

- **Risco de Linhas Fantasmas (Tratado mas Crítico):**
  - O duplo filtro (Frontend no `getTableDataForSubmission` e Backend no `salvar.php`) lida com isso. No entanto, se o usuário preencher uma coluna não coberta pelos filtros de "vazio" e o backend não validar, o JSON pode persistir blocos de informações em branco.
  - **Cuidado:** Ao alterar o layout da tabela, o script `reindexarTabela.js` (ou `dataManager.recalcularIndices()`) **deve ser atualizado ou invocado** para não causar descompasso no `name="array[]"` das linhas se novos campos forem injetados.
- **Integridade Decimal (Sincronismo JS vs PHP):**
  - O JS envia o dado sanitizado formatado usando `replace(",", ".")` no `getTableDataForSubmission.js`.
  - **Cuidado:** O backend PHP confia plenamente nesse payload JSON empacotado. Se novas colunas monetárias ou de porcentagem forem adicionadas sem o devido `replace`, o banco salvará a string como "R$ 1.500,20", quebrando cálculos futuros (ex: relatórios) que esperam um float nativo.
- **Performance do Banco (Queries em Loops Evitadas):**
  - Atualmente, o loop `foreach ($itensValidos as $linha)` gerando múltiplos `INSERT` na tabela `respostas_tabela_dinamica` (que existia em abordagens legadas e em `4_salvar_perguntas.php`) foi contornado no `salvar.php` adotando o salvamento em um único campo JSON da `respostas_dinamicas`.
  - **Cuidado:** Se for necessário voltar ao mapeamento relacional (uma linha do banco para cada linha da tabela JS), será estritamente necessário usar Prepared Statements com _transactions_ ou _Bulk Inserts_ (`INSERT INTO ... VALUES (), (), ()`) para evitar degradação de performance (timeouts no fetch do JS).
- **Hidratação de Dados (DataHydrator.js):**
  - Sempre que adicionar ou modificar lógicas que leem valores (ex: "Buscar Valores do Slugs do Excel"), a tradução entre "Slug Legado" e "ID Estável" feita pelo `DataHydrator` é o único elo seguro para garantir compatibilidade retroativa. Nunca ignore esse passo.
